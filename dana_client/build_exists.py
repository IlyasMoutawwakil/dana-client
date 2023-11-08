import os
from requests import Session
from argparse import ArgumentParser

from .base import authenticate, get_project, get_build


def main():
    parser = ArgumentParser()

    parser.add_argument("--dana-url", type=str, required=True)
    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--build-id", type=int, required=True)

    args = parser.parse_args()

    dana_url = args.dana_url
    project_id = args.project_id
    build_id = args.build_id

    API_TOKEN = os.environ.get("API_TOKEN", None)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

    session = Session()

    session = authenticate(
        session=session,
        dana_url=dana_url,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        api_token=API_TOKEN,
    )

    get_project(
        session=session,
        dana_url=dana_url,
        api_token=API_TOKEN,
        project_id=project_id,
    )

    get_build(
        session=session,
        dana_url=dana_url,
        api_token=API_TOKEN,
        project_id=project_id,
        build_id=build_id,
    )
