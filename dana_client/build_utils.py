import os
import json
from pathlib import Path
from requests import Session
from argparse import ArgumentParser

from huggingface_hub import HfApi
from omegaconf import OmegaConf
import pandas as pd

from .api import add_project, add_build, add_series, add_sample, project_exists


def upload_build(
    folder: Path,
    dataset_id: str,
    hf_token: str,
    project_id: str,
    build_id: int,
    build_url: str,
    build_hash: str,
    build_abbrev_hash: str,
    build_author_name: str,
    build_author_email: str,
    build_subject: str,
) -> None:
    """
    Uploads the folder to the HuggingFace dataset.
    """
    build_info = {
        "build_url": build_url,
        "build_hash": build_hash,
        "build_subject": build_subject,
        "build_abbrev_hash": build_abbrev_hash,
        "build_author_name": build_author_name,
        "build_author_email": build_author_email,
    }

    with open(folder / "build_info.json", "w") as f:
        json.dump(build_info, f)

    HfApi().upload_folder(
        repo_id=dataset_id,
        folder_path=folder,  # path to the folder you want to upload
        path_in_repo=f"{project_id}/{build_id}",
        delete_patterns="*",  # to rewrite the folder
        repo_type="dataset",
        token=hf_token,
    )


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
