import os
from requests import Session
from argparse import ArgumentParser

from .base import authenticate, get_project, get_build

HF_TOKEN = os.environ.get("HF_TOKEN", None)
API_TOKEN = os.environ.get("API_TOKEN", None)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")


def main():
    parser = ArgumentParser()

    parser.add_argument("--dana-url", type=str, required=True)
    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--build-id", type=int, required=True)

    args = parser.parse_args()

    dana_url = args.dana_url
    project_id = args.project_id
    build_id = args.build_id

    session = Session()

    session = authenticate(
        session=session,
        dana_url=dana_url,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        auth_token=HF_TOKEN,
    )

    _ = get_project(
        session=session,
        dana_url=dana_url,
        api_token=API_TOKEN,
        project_id=project_id,
    )

    _ = get_build(
        session=session,
        dana_url=dana_url,
        api_token=API_TOKEN,
        project_id=project_id,
        build_id=build_id,
    )
