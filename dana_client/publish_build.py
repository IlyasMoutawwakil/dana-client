import os
from pathlib import Path
from requests import Session
from argparse import ArgumentParser

from omegaconf import OmegaConf
import pandas as pd

from .api import login, add_project, add_build, add_series, add_sample, project_exists


def publish_build(
    url: str,
    session: Session,
    api_token: str,
    folder: Path,
    project_id: str,
    build_id: int,
    build_url: str = "",
    build_hash: str = "",
    build_abbrev_hash: str = "",
    build_author_name: str = "",
    build_author_email: str = "",
    build_subject: str = "",
    average_range: str = "5%",
    average_min_count: int = 3,
) -> None:
    p_exists = project_exists(
        session=session,
        url=url,
        api_token=api_token,
        project_id=project_id,
    )
    if not p_exists:
        add_project(
            session=session,
            url=url,
            api_token=api_token,
            project_id=project_id,
            users="",
            project_description="",
            override=True,
        )

    add_build(
        session=session,
        url=url,
        api_token=api_token,
        project_id=project_id,
        build_id=build_id,
        build_url=build_url,
        build_hash=build_hash,
        build_subject=build_subject,
        build_abbrev_hash=build_abbrev_hash,
        build_author_name=build_author_name,
        build_author_email=build_author_email,
        override=True,
    )
    for benchmark_foler in folder.iterdir():
        if not benchmark_foler.is_dir():
            continue

        inference_results = list(benchmark_foler.glob("**/inference_results.csv"))
        hydra_config = list(benchmark_foler.glob("**/hydra_config.yaml"))

        if len(inference_results) != 1 or len(hydra_config) != 1:
            continue

        inference_results = pd.read_csv(inference_results[0]).to_dict(orient="records")
        series_description = OmegaConf.to_yaml(OmegaConf.load(hydra_config[0])).replace(
            "\n", "<br>"
        )

        # Latency series
        latency_ms = inference_results[0]["forward.latency(s)"] * 1000
        series_id = f"{benchmark_foler.name}_latency(ms)"
        add_series(
            session=session,
            api_token=api_token,
            url=url,
            project_id=project_id,
            series_id=series_id,
            series_unit="ms",
            series_description=series_description,
            benchmark_range=average_range,
            benchmark_required=average_min_count,
            benchmark_trend="smaller",
            override=True,
        )

        add_sample(
            session=session,
            url=url,
            api_token=api_token,
            project_id=project_id,
            build_id=build_id,
            series_id=series_id,
            sample_value=latency_ms,
            sample_unit="ms",
            override=True,
        )

        # Memory series
        if "forward.peak_memory(MB)" in inference_results[0]:
            memory_mb = inference_results[0]["forward.peak_memory(MB)"]

            series_id = f"{benchmark_foler.name}_memory(mbytes)"
            add_series(
                session=session,
                url=url,
                api_token=api_token,
                project_id=project_id,
                series_id=series_id,
                series_unit="mbytes",
                series_description=series_description,
                benchmark_range=average_range,
                benchmark_required=average_min_count,
                benchmark_trend="smaller",
                override=True,
            )
            add_sample(
                session=session,
                url=url,
                api_token=api_token,
                project_id=project_id,
                build_id=build_id,
                series_id=series_id,
                sample_value=memory_mb,
                sample_unit="mbytes",
                override=True,
            )

        # Throughput series
        if "generate.throughput(tokens/s)" in inference_results[0]:
            throughput_tok_s = inference_results[0]["generate.throughput(tokens/s)"]

            series_id = f"{benchmark_foler.name}_throughput(tokens)"
            add_series(
                session=session,
                url=url,
                api_token=api_token,
                project_id=project_id,
                series_id=series_id,
                series_unit="tokens",
                series_description=series_description,
                benchmark_range=average_range,
                benchmark_required=average_min_count,
                benchmark_trend="higher",
                override=True,
            )

            add_sample(
                session=session,
                url=url,
                api_token=api_token,
                project_id=project_id,
                build_id=build_id,
                series_id=series_id,
                sample_value=throughput_tok_s,
                sample_unit="tokens",
                override=True,
            )


def main():
    parser = ArgumentParser()

    parser.add_argument("--folder", type=Path, required=True)

    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--build-id", type=int, required=True)

    parser.add_argument("--build-url", type=str, default="")
    parser.add_argument("--build-hash", type=str, default="")
    parser.add_argument("--build-subject", type=str, default="")
    parser.add_argument("--build-abbrev-hash", type=str, default="")
    parser.add_argument("--build-author-name", type=str, default="")
    parser.add_argument("--build-author-email", type=str, default="")

    parser.add_argument("--average-range", type=str, default="5%")
    parser.add_argument("--average-min-count", type=int, default=3)

    args = parser.parse_args()

    folder = args.folder

    url = args.url
    project_id = args.project_id
    build_id = args.build_id

    build_url = args.build_url
    build_hash = args.build_hash
    build_subject = args.build_subject
    build_abbrev_hash = args.build_abbrev_hash
    build_author_name = args.build_author_name
    build_author_email = args.build_author_email

    average_range = args.average_range
    average_min_count = args.average_min_count

    API_TOKEN = os.environ.get("API_TOKEN", None)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

    session = login(
        url=url,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    publish_build(
        url=url,
        session=session,
        api_token=API_TOKEN,
        folder=folder,
        project_id=project_id,
        build_id=build_id,
        build_url=build_url,
        build_hash=build_hash,
        build_subject=build_subject,
        build_abbrev_hash=build_abbrev_hash,
        build_author_name=build_author_name,
        build_author_email=build_author_email,
        average_range=average_range,
        average_min_count=average_min_count,
    )
