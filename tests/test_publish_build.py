from requests.exceptions import HTTPError
from pathlib import Path

import pytest

from dana_client.api import login, build_exists
from dana_client.publish_build import publish_build

FOLDER = Path("experiments")
URL = "http://localhost:7000"
PROJECT_ID = "test-publish-build-project"
BUILD_ID = 1

API_TOKEN = "api-token"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


def test_publish_build():
    
    session = login(
        url=URL,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    publish_build(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        folder=FOLDER,
        project_id=PROJECT_ID,
        build_id=BUILD_ID,
        build_url="",
        build_hash="",
        build_subject="",
        build_abbrev_hash="",
        build_author_name="",
        build_author_email="",
        average_range="5%",
        average_min_count=3,
    )

    assert (
        build_exists(
            url=URL,
            session=session,
            api_token=API_TOKEN,
            project_id=PROJECT_ID,
            build_id=BUILD_ID,
        )
        is True
    )


def test_publish_build_wrong_token():
    session = login(
        url=URL,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    with pytest.raises(HTTPError):
        publish_build(
            folder=FOLDER,
            session=session,
            url=URL,
            api_token="wrong-token",
            project_id=PROJECT_ID,
            build_id=BUILD_ID,
            build_url="",
            build_hash="",
            build_subject="",
            build_abbrev_hash="",
            build_author_name="",
            build_author_email="",
            average_range="5%",
            average_min_count=3,
        )
