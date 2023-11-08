import os
import json
from pathlib import Path
from requests import Session
from argparse import ArgumentParser

from huggingface_hub import snapshot_download

from .base import LOGGER, authenticate, add_new_project
from .publish_build import publish_build


def main():
    parser = ArgumentParser()

    parser.add_argument("--dana-url", type=str, required=True)
    parser.add_argument("--dana-dataset-id", type=str, required=True)

    args = parser.parse_args()

    dana_url = args.dana_url
    dana_dataset_id = args.dana_dataset_id

    HF_TOKEN = os.environ.get("HF_TOKEN", None)
    API_TOKEN = os.environ.get("API_TOKEN", None)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

    session = Session()
    LOGGER.info(" + Authenticating")
    authenticate(
        session=session,
        dana_url=dana_url,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        api_token=API_TOKEN,
    )

    LOGGER.info("Downloading backup dataset")
    dataset_path = Path(
        snapshot_download(
            repo_id=dana_dataset_id,
            repo_type="dataset",
            token=HF_TOKEN,
        )
    )

    LOGGER.info("Publishing backup dataset")
    for project_path in dana_dataset_id.iterdir():
        if not project_path.is_dir():
            continue

        project_id = project_path.name
        project_info = json.load(open(project_path / "project_info.json"))

        add_new_project(
            session=session,
            dana_url=dana_url,
            api_token=API_TOKEN,
            project_id=project_id,
            users=project_info["users"],
            project_description=project_info["project_description"],
            override=True,
        )

        for build_path in project_path.iterdir():
            if not build_path.is_dir():
                continue

            LOGGER.info(f" + Getting build info from {build_path / 'build_info.json'}")
            build_info = json.load(open(build_path / "build_info.json"))

            build_id = int(build_path.name)
            LOGGER.info(f" + Publishing build {build_id}")
            publish_build(
                session=session,
                dana_url=dana_url,
                api_token=API_TOKEN,
                project_id=project_id,
                build_id=build_id,
                build_info=build_info,
                build_folder=build_path,
            )

    LOGGER.info("Finished publishing backup dataset")
