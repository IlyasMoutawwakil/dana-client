import json
from typing import Any, Dict
from requests import Session, Response
from requests.exceptions import ConnectionError, HTTPError


def get(
    session: Session,
    url: str,
    api_token: str,
    payload: Dict[str, Any],
) -> Response:
    data = json.dumps(payload)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    response = session.get(url=url, data=data, headers=headers)

    code = response.status_code
    if code != 200:
        raise HTTPError(f"API get request to {url} failed with code {code}")

    return response


def post(
    session: Session,
    url: str,
    api_token: str,
    payload: Dict[str, Any],
) -> Response:
    data = json.dumps(payload)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }

    response = session.post(url=url, data=data, headers=headers)

    code = response.status_code
    if code != 200:
        raise HTTPError(f"API post request to {url} failed with code {code}")

    return response


def login(
    url: str,
    api_token: str,
    username: str,
    password: str,
) -> Session:
    session = Session()
    login_url = f"{url}/login"
    login_payload = {"username": username, "password": password}

    login_response = post(
        session=session,
        url=login_url,
        api_token=api_token,
        payload=login_payload,
    )

    if login_response.url == login_url:
        raise ConnectionError(f"Login to {url} redirected to login page")

    return session


def add_project(
    url: str,
    session: Session,
    api_token: str,
    project_id: str,
    users: str = "",
    project_description: str = "",
    override: bool = False,
) -> Response:
    project_url = f"{url}/admin/addProject"
    project_payload = {
        "projectId": project_id,
        "users": users,
        "description": project_description,
        "override": override,
    }
    project_response = post(
        session=session,
        url=project_url,
        api_token=api_token,
        payload=project_payload,
    )

    return project_response


def add_build(
    session: Session,
    url: str,
    api_token: str,
    project_id: str,
    build_id: str,
    build_url: str = "",
    build_hash: str = "",
    build_subject: str = "",
    build_abbrev_hash: str = "",
    build_author_name: str = "",
    build_author_email: str = "",
    override: bool = False,
) -> Response:
    build_url = f"{url}/apis/addBuild"
    build_payload = {
        "projectId": project_id,
        "build": {
            "buildId": build_id,
            "infos": {
                "url": build_url,
                "hash": build_hash,
                "subject": build_subject,
                "abbrevHash": build_abbrev_hash,
                "authorName": build_author_name,
                "authorEmail": build_author_email,
            },
        },
        "override": override,
    }

    build_response = post(
        session=session,
        url=build_url,
        api_token=api_token,
        payload=build_payload,
    )

    return build_response


def add_series(
    session: Session,
    url: str,
    api_token: str,
    project_id: str,
    series_id: str,
    series_unit: str = "ms",
    series_description: str = "",
    benchmark_range: str = "5%",
    benchmark_required: int = 3,
    benchmark_trend: str = "smaller",
    override: bool = False,
) -> Response:
    series_url = f"{url}/apis/addSerie"
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
        "description": series_description,
    }
    series_response = post(
        session=session,
        url=series_url,
        api_token=api_token,
        payload=series_payload,
    )

    return series_response


def add_sample(
    session: Session,
    url: str,
    api_token: str,
    project_id: str,
    build_id: str,
    series_id: str,
    sample_value: int,
    sample_unit: str = "ms",
    override: bool = False,
) -> Response:
    sample_url = f"{url}/apis/addSample"
    sample_payload = {
        "projectId": project_id,
        "serieId": series_id,
        "sampleUnit": sample_unit,
        "sample": {"buildId": build_id, "value": sample_value},
        "override": override,
    }

    sample_response = post(
        session=session,
        url=sample_url,
        api_token=api_token,
        payload=sample_payload,
    )

    return sample_response


def project_exists(
    url: str,
    session: Session,
    api_token: str,
    project_id: str,
) -> bool:
    project_url = f"{url}/apis/getBuild"
    project_payload = {"projectId": project_id, "buildId": 0}

    try:
        get(
            session=session,
            url=project_url,
            api_token=api_token,
            payload=project_payload,
        )
        return True
    except HTTPError:
        return False


def build_exists(
    url: str,
    session: Session,
    api_token: str,
    project_id: str,
    build_id: str,
) -> bool:
    build_url = f"{url}/apis/getBuild"
    build_payload = {"projectId": project_id, "buildId": build_id}

    build_response = get(
        session=session,
        url=build_url,
        api_token=api_token,
        payload=build_payload,
    )
    build_response = build_response.json()

    if len(build_response) > 0:
        return True
    else:
        return False
