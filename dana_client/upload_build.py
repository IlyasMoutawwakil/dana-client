import os
import json
from pathlib import Path
from argparse import ArgumentParser

from huggingface_hub import HfApi


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


def main():
    parser = ArgumentParser()

    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--dataset-id", type=str, required=True)

    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--build-id", type=int, required=True)

    parser.add_argument("--build-hash", type=str, required=True)
    parser.add_argument("--build-abbrev-hash", type=str, required=True)
    parser.add_argument("--build-author-name", type=str, required=True)
    parser.add_argument("--build-author-email", type=str, required=True)
    parser.add_argument("--build-subject", type=str, required=True)
    parser.add_argument("--build-url", type=str, required=True)

    parser.add_argument("--average-range", type=int, default=5)
    parser.add_argument("--average-min-count", type=int, default=3)

    args = parser.parse_args()

    folder = args.folder
    dataset_id = args.dataset_id

    project_id = args.project_id
    build_id = args.build_id

    build_hash = args.build_hash
    build_abbrev_hash = args.build_abbrev_hash
    build_author_name = args.build_author_name
    build_author_email = args.build_author_email
    build_subject = args.build_subject
    build_url = args.build_url

    HF_TOKEN = os.environ.get("HF_TOKEN", None)

    upload_build(
        folder=folder,
        dataset_id=dataset_id,
        hf_token=HF_TOKEN,
        project_id=project_id,
        build_id=build_id,
        build_url=build_url,
        build_hash=build_hash,
        build_abbrev_hash=build_abbrev_hash,
        build_author_name=build_author_name,
        build_author_email=build_author_email,
        build_subject=build_subject,
    )
