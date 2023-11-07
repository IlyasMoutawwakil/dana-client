import json
import logging
from requests import Session
from typing import Any, Dict, Optional

import coloredlogs


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("dana-client")
coloredlogs.install(level="INFO", logger=LOGGER)


def authenticate(
    session: Session,
    dana_url: str,
    username: str,
    password: str,
    auth_token: Optional[str] = None,
) -> Session:
    session.post(
        f"{dana_url}/login",
        data=json.dumps({"username": username, "password": password}),
        headers={
            "Content-Type": "application/json",
            **(
                {"Authorization": f"Bearer {auth_token}"}
                if auth_token is not None
                else {}
            ),
        },
    )

    return session


def post_to_dana(
    session: Session,
    dana_url: str,
    api_token: str,
    payload: Dict[str, Any],
) -> None:
    data = json.dumps(payload)

    response = session.post(
        dana_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
        },
    )

    code = response.status_code
    LOGGER.info(f"API response code: {code}")

    if code != 200:
        raise RuntimeError("API request failed")


def get_from_dana(
    session: Session,
    dana_url: str,
    api_token: str,
    payload: Dict[str, Any],
) -> None:
    data = json.dumps(payload)

    response = session.get(
        dana_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
        },
    )

    code = response.status_code
    LOGGER.info(f"API response code: {code}")

    if code != 200:
        raise RuntimeError("API request failed")

    return response.json()


def add_new_project(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
    users: str = "",
    project_description: str = "",
    override: bool = False,
) -> None:
    dana_project_url = f"{dana_url}/admin/addProject"
    project_payload = {
        "projectId": project_id,
        "users": users,
        "description": project_description,
        "override": override,
    }

    post_to_dana(
        session=session,
        dana_url=dana_project_url,
        api_token=api_token,
        payload=project_payload,
    )


def get_project(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
) -> None:
    dana_project_url = f"{dana_url}/apis/getProject"
    project_payload = {"projectId": project_id, "buildId": 0}

    project = get_from_dana(
        session=session,
        dana_url=dana_project_url,
        api_token=api_token,
        payload=project_payload,
    )

    return project


def add_new_build(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
    build_id: str,
    build_hash: str,
    build_abbrev_hash: str,
    build_author_name: str,
    build_author_email: str,
    build_subject: str,
    build_url: str,
    override: bool = False,
) -> None:
    dana_build_url = f"{dana_url}/apis/addBuild"
    build_payload = {
        "projectId": project_id,
        "build": {
            "buildId": build_id,
            "infos": {
                "hash": build_hash,
                "abbrevHash": build_abbrev_hash,
                "authorName": build_author_name,
                "authorEmail": build_author_email,
                "subject": build_subject,
                "url": build_url,
            },
        },
        "override": override,
    }

    post_to_dana(
        session=session,
        dana_url=dana_build_url,
        api_token=api_token,
        payload=build_payload,
    )


def get_build(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
    build_id: str,
) -> None:
    dana_build_url = f"{dana_url}/apis/getBuild"
    build_payload = {"projectId": project_id, "buildId": build_id}

    build = get_from_dana(
        session=session,
        dana_url=dana_build_url,
        api_token=api_token,
        payload=build_payload,
    )

    if len(build) == 0:
        raise RuntimeError(f"Failed to get build {build_id}")

    return build


def add_new_series(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
    series_id: str,
    series_unit: str,
    benchmark_range: int,
    benchmark_required: int,
    benchmark_trend: str = "lower",
    series_description: Optional[str] = None,
    override: bool = False,
) -> None:
    dana_series_url = f"{dana_url}/apis/addSerie"
    series_payload = {
        "projectId": project_id,
        "serieId": series_id,
        "serieUnit": series_unit,
        "analyse": {
            "benchmark": {
                "range": benchmark_range,
                "required": benchmark_required,
                "trend": benchmark_trend,
            }
        },
        "override": override,
    }

    if series_description is not None:
        series_payload["description"] = series_description

    post_to_dana(
        session=session,
        dana_url=dana_series_url,
        api_token=api_token,
        payload=series_payload,
    )


def add_new_sample(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
    build_id: str,
    series_id: str,
    sample_value: int,
    override: bool = False,
) -> None:
    dana_sample_url = f"{dana_url}/apis/addSample"
    sample_payload = {
        "projectId": project_id,
        "serieId": series_id,
        "sample": {"buildId": build_id, "value": sample_value},
        "override": override,
    }

    post_to_dana(
        session=session,
        dana_url=dana_sample_url,
        api_token=api_token,
        payload=sample_payload,
    )
