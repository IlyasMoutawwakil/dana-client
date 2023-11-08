import os
import json
import shutil
from pathlib import Path
from requests import Session
from argparse import ArgumentParser

from huggingface_hub import HfApi
from omegaconf import OmegaConf
import pandas as pd

from .base import LOGGER, authenticate, add_new_sample, add_new_build, add_new_series


def publish_build(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
    build_id: int,
    build_info: dict,
    build_folder: Path,
    average_range: int = 5,
    average_min_count: int = 3,
) -> None:
    LOGGER.info(f" + Publishing build {build_id}")
    add_new_build(
        session=session,
        dana_url=dana_url,
        api_token=api_token,
        project_id=project_id,
        build_id=build_id,
        build_url=build_info["build_url"],
        build_hash=build_info["build_hash"],
        build_abbrev_hash=build_info["build_abbrev_hash"],
        build_author_name=build_info["build_author_name"],
        build_author_email=build_info["build_author_email"],
        build_subject=build_info["build_subject"],
        override=True,
    )
    for series_foler in build_folder.iterdir():
        if not series_foler.is_dir():
            continue

        configs = list(series_foler.glob("*/hydra_config.yaml"))
        inference_results = list(series_foler.glob("*/inference_results.csv"))

        if len(inference_results) != 1 or len(configs) != 1:
            LOGGER.info(f" + Skipping {series_foler.name}")
            shutil.rmtree(series_foler)
            continue

        series_description = OmegaConf.to_yaml(OmegaConf.load(configs[0]))
        inference_results = pd.read_csv(inference_results[0]).to_dict(orient="records")

        # Latency series
        latency_ms = inference_results[0]["forward.latency(s)"] * 1000

        series_id = f"{series_foler.name}_latency(ms)"
        LOGGER.info(f"\t + Publishing series {series_id}")
        add_new_series(
            session=session,
            api_token=api_token,
            dana_url=dana_url,
            project_id=project_id,
            series_id=series_id,
            series_unit="ms",
            series_description=series_description,
            benchmark_range=average_range,
            benchmark_required=average_min_count,
            benchmark_trend="smaller",
            override=True,
        )

        LOGGER.info(
            f"\t + Publishing sample for series {series_id} and build {build_id}"
        )
        add_new_sample(
            session=session,
            dana_url=dana_url,
            api_token=api_token,
            project_id=project_id,
            build_id=build_id,
            series_id=series_id,
            sample_value=latency_ms,
            override=True,
        )

        # Memory series
        if "forward.peak_memory(MB)" in inference_results[0]:
            memory_mb = inference_results[0]["forward.peak_memory(MB)"]

            series_id = f"{series_foler.name}_memory(MB)"
            LOGGER.info(f"\t + Publishing series {series_id}")
            add_new_series(
                session=session,
                dana_url=dana_url,
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

            LOGGER.info(
                f"\t + Publishing sample for series {series_id} and build {build_id}"
            )
            add_new_sample(
                session=session,
                dana_url=dana_url,
                api_token=api_token,
                project_id=project_id,
                build_id=build_id,
                series_id=series_id,
                sample_value=memory_mb,
                override=True,
            )

        # Throughput series
        if "generate.throughput(tokens/s)" in inference_results[0]:
            throughput_tok_s = inference_results[0]["generate.throughput(tokens/s)"]

            series_id = f"{series_foler.name}_throughput(tokens.s-1)"
            LOGGER.info(f"\t+ Publishing series {series_id}")
            add_new_series(
                session=session,
                dana_url=dana_url,
                api_token=api_token,
                project_id=project_id,
                series_id=series_id,
                series_unit="ns",
                series_description=series_description,
                benchmark_range=average_range,
                benchmark_required=average_min_count,
                benchmark_trend="higher",
                override=True,
            )

            LOGGER.info(f"\t+ Publishing sample for series {series_id}")
            add_new_sample(
                session=session,
                dana_url=dana_url,
                api_token=api_token,
                project_id=project_id,
                build_id=build_id,
                series_id=series_id,
                sample_value=throughput_tok_s,
                override=True,
            )


def main():
    parser = ArgumentParser()

    parser.add_argument("--build-folder", type=Path, required=True)

    parser.add_argument("--dana-url", type=str, required=True)
    parser.add_argument("--dana-dataset-id", type=str, required=True)

    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--build-id", type=int, required=True)

    parser.add_argument("--build-hash", type=str, required=True)
    parser.add_argument("--build-abbrev-hash", type=str, required=True)
    parser.add_argument("--build-author-name", type=str, required=True)
    parser.add_argument("--build-author-email", type=str, required=True)
    parser.add_argument("--build-subject", type=str, required=True)
    parser.add_argument("--build-url", type=str, required=True)

    args = parser.parse_args()

    dana_url = args.dana_url
    dana_dataset_id = args.dana_dataset_id
    build_folder = args.build_folder
    project_id = args.project_id
    build_id = args.build_id

    build_info = {
        "build_hash": args.build_hash,
        "build_abbrev_hash": args.build_abbrev_hash,
        "build_author_name": args.build_author_name,
        "build_author_email": args.build_author_email,
        "build_subject": args.build_subject,
        "build_url": args.build_url,
    }

    AVERAGE_RANGE = 5  # 5 percent
    AVERAGE_MIN_COUNT = 3  # 3 samples
    HF_TOKEN = os.environ.get("HF_TOKEN", None)
    API_TOKEN = os.environ.get("API_TOKEN", None)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

    session = Session()

    LOGGER.info(" + Authenticating to DANA dashboard")
    authenticate(
        session=session,
        dana_url=dana_url,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        api_token=API_TOKEN,
    )

    LOGGER.info(" + Uploading benchmark to HF dataset")
    LOGGER.info(" + Saving build info")
    with open(build_folder / "build_info.json", "w") as f:
        json.dump(build_info, f)

    LOGGER.info(" + Uploading experiments folder")
    HfApi().upload_folder(
        repo_id=dana_dataset_id,
        folder_path=build_folder,  # path to the folder you want to upload
        path_in_repo=f"{project_id}/{build_id}",
        delete_patterns="*",  # to rewrite the folder
        repo_type="dataset",
        token=HF_TOKEN,
    )

    LOGGER.info(" + Publishing benchmark to DANA server")
    publish_build(
        session=session,
        dana_url=dana_url,
        api_token=API_TOKEN,
        project_id=project_id,
        build_id=build_id,
        build_info=build_info,
        build_folder=build_folder,
        average_range=AVERAGE_RANGE,
        average_min_count=AVERAGE_MIN_COUNT,
    )
