import os
import json
from pathlib import Path
from requests import Session
from argparse import ArgumentParser

from huggingface_hub import snapshot_download

from .api import login
from .build_utils import publish_build


def publish_backup(
    url: str,
    session: Session,
    hf_token: str,
    api_token: str,
    dataset_id: str,
):
    """
    Publishes a backup dataset to DANA server.
    """

    dataset_path = Path(
        snapshot_download(
            repo_id=dataset_id,
            repo_type="dataset",
            token=hf_token,
        )
    )
    for project_path in dataset_path.iterdir():
        if not project_path.is_dir():
            continue
        for build_path in project_path.iterdir():
            if not build_path.is_dir():
                continue

            project_id = project_path.name
            build_id = int(build_path.name)

            build_info = json.load(open(build_path / "build_info.json"))

            # publish the build
            publish_build(
                folder=build_path,
                url=url,
                session=session,
                api_token=api_token,
                project_id=project_id,
                build_id=build_id,
                build_url=build_info["build_url"],
                build_hash=build_info["build_hash"],
                build_subject=build_info["build_subject"],
                build_abbrev_hash=build_info["build_abbrev_hash"],
                build_author_name=build_info["build_author_name"],
                build_author_email=build_info["build_author_email"],
                average_range="5%",
                average_min_count=3,
            )


def main():
    parser = ArgumentParser()

    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--dataset-id", type=str, required=True)

    args = parser.parse_args()

    url = args.url
    dataset_id = args.dataset_id

    HF_TOKEN = os.environ.get("HF_TOKEN", None)
    API_TOKEN = os.environ.get("API_TOKEN", None)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

    session = login(
        url=url,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    publish_backup(
        url=url,
        session=session,
        hf_token=HF_TOKEN,
        api_token=API_TOKEN,
        dataset_id=dataset_id,
    )
