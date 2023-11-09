from requests import Session
from requests.exceptions import ConnectionError, HTTPError

import pytest

from dana_client.api import (
    login,
    add_project,
    add_build,
    add_series,
    add_sample,
    project_exists,
    build_exists,
)

URL = "http://localhost:7000"
PROJECT_ID = "test-api-project"
SERIES_ID = "test-api-series"
API_TOKEN = "api-token"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


def test_login():
    session = login(
        url=URL,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )


def test_login_wrong_credentials():
    with pytest.raises(ConnectionError):
        session = login(
            url=URL,
            api_token=API_TOKEN,
            username=ADMIN_USERNAME,
            password="wrong-password",
        )

    with pytest.raises(ConnectionError):
        session = login(
            url=URL,
            api_token=API_TOKEN,
            username="wrong-username",
            password=ADMIN_PASSWORD,
        )


def test_add_project():
    session = login(
        url=URL,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    add_project(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        project_description="",
        override=True,
    )


def test_add_build():
    session = login(
        url=URL,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    add_project(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        project_description="",
        override=True,
    )

    add_build(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        build_id=1,
        build_url="",
        build_hash="",
        build_abbrev_hash="",
        build_author_name="",
        build_author_email="",
        build_subject="",
        override=True,
    )


def test_add_series():
    session = login(
        url=URL,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    add_project(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        project_description="",
        override=True,
    )

    add_series(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        series_id=SERIES_ID,
        series_unit="tokens",
        series_description="",
        benchmark_range="5%",
        benchmark_required=3,
        benchmark_trend="higher",
        override=True,
    )


def test_add_sample():
    session = login(
        url=URL,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    add_project(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        project_description="",
        override=True,
    )

    add_series(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        series_id=SERIES_ID,
        series_unit="tokens",
        series_description="",
        benchmark_range="5%",
        benchmark_required=3,
        benchmark_trend="higher",
        override=True,
    )

    add_build(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        build_id=1,
        build_url="",
        build_hash="",
        build_abbrev_hash="",
        build_author_name="",
        build_author_email="",
        build_subject="",
        override=True,
    )

    add_sample(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        series_id=SERIES_ID,
        build_id=1,
        sample_value=1000,
        sample_unit="tokens",
        override=True,
    )


def test_project_exists():
    session = login(
        url=URL,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    add_project(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        project_description="",
        override=True,
    )

    assert (
        project_exists(
            url=URL,
            session=session,
            api_token=API_TOKEN,
            project_id=PROJECT_ID,
        )
        is True
    )

    assert (
        project_exists(
            url=URL,
            session=session,
            api_token=API_TOKEN,
            project_id="not-test-project",
        )
        is False
    )


def test_build_exists():
    session = login(
        url=URL,
        api_token=API_TOKEN,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    add_project(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        project_description="",
        override=True,
    )

    add_build(
        url=URL,
        session=session,
        api_token=API_TOKEN,
        project_id=PROJECT_ID,
        build_id=1,
        build_url="",
        build_hash="",
        build_abbrev_hash="",
        build_author_name="",
        build_author_email="",
        build_subject="",
        override=True,
    )

    assert (
        build_exists(
            url=URL,
            session=session,
            api_token=API_TOKEN,
            project_id=PROJECT_ID,
            build_id=1,
        )
        is True
    )

    assert (
        build_exists(
            url=URL,
            session=session,
            api_token=API_TOKEN,
            project_id=PROJECT_ID,
            build_id=2,
        )
        is False
    )
