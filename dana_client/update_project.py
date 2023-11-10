import os
import shutil
import subprocess
from pathlib import Path
from requests import Session
from argparse import ArgumentParser

from git import Repo

from .api import login, build_exists, project_exists, add_project
from .build_utils import publish_build, upload_build


def update_project(
    url: str,
    session: Session,
    api_token: str,
    dataset_id: str,
    hf_token: str,
    project_id: str,
    watch_repo: str,
    num_commits: int = 10,
    average_range: str = "5%",
    average_min_count: int = 3,
    debug: bool = False,
):
    """
    Updates a dana project that's monitoring a git repository.
    """

    p_exists = project_exists(
        url=url,
        session=session,
        api_token=api_token,
        project_id=project_id,
    )
    if not p_exists:
        add_project(
            url=url,
            session=session,
            api_token=api_token,
            project_id=project_id,
            override=True,
        )

    try:
        repo = Repo.clone_from(watch_repo, "watch_repo")
    except Exception:
        repo = Repo("watch_repo")

    commits = repo.iter_commits("main", max_count=num_commits)

    for commit in commits:
        build_id = str(commit.count())

        # check if build exists
        b_exists = build_exists(
            url=url,
            session=session,
            api_token=api_token,
            project_id=project_id,
            build_id=build_id,
        )
        if b_exists:
            continue

        # get build info
        build_hash = commit.hexsha
        build_abbrev_hash = commit.hexsha[:7]
        build_author_name = commit.author.name
        build_author_email = commit.author.email
        build_subject = commit.message
        build_url = f"{watch_repo}/commit/{commit}"

        repo.git.checkout(build_hash)
        # run the install command and omit stdout (devnull)
        out = subprocess.run(
            ["pip", "install", "-e", "watch_repo"],
            stdout=subprocess.DEVNULL if not debug else None,
            stderr=subprocess.STDOUT if not debug else None,
        )

        if out.returncode != 0:
            raise RuntimeError("Install failed!")

        # run the benchmarks
        for config_file in os.listdir("benchmarks"):
            # get config name
            config_name = os.path.splitext(config_file)[0]
            # skip _base_
            if config_name == "_base_":
                continue

            # omit stdout (devnull)
            out = subprocess.run(
                [
                    "optimum-benchmark",
                    "--config-dir",
                    "benchmarks",
                    "--config-name",
                    config_name,
                    "--multirun",
                ],
                stdout=subprocess.DEVNULL if not debug else None,
                stderr=subprocess.STDOUT if not debug else None,
            )

            if out.returncode != 0:
                raise RuntimeError("Benchmark failed!")

        # upload the build
        upload_build(
            folder=Path("experiments"),
            dataset_id=dataset_id,
            hf_token=hf_token,
            project_id=project_id,
            build_id=build_id,
            build_url=build_url,
            build_hash=build_hash,
            build_subject=build_subject,
            build_abbrev_hash=build_abbrev_hash,
            build_author_name=build_author_name,
            build_author_email=build_author_email,
        )

        # publish the build
        publish_build(
            folder=Path("experiments"),
            url=url,
            session=session,
            api_token=api_token,
            project_id=project_id,
            build_id=build_id,
            build_url=build_url,
            build_hash=build_hash,
            build_subject=build_subject,
            build_abbrev_hash=build_abbrev_hash,
            build_author_name=build_author_name,
            build_author_email=build_author_email,
            average_range=average_range,
            average_min_count=average_min_count,
        )

        shutil.rmtree("experiments")


def main():
    parser = ArgumentParser()

    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--dataset-id", type=str, required=True)
    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--watch-repo", type=str, required=True)
    parser.add_argument("--num-commits", type=int, default=10)
    parser.add_argument("--average-range", type=str, default="5%")
    parser.add_argument("--average-min-count", type=int, default=3)
    parser.add_argument("--debug", action="store_true", default=False)

    args = parser.parse_args()

    url = args.url
    dataset_id = args.dataset_id
    project_id = args.project_id
    watch_repo = args.watch_repo
    num_commits = args.num_commits
    average_range = args.average_range
    average_min_count = args.average_min_count
    debug = args.debug

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

    update_project(
        url=url,
        session=session,
        api_token=API_TOKEN,
        dataset_id=dataset_id,
        hf_token=HF_TOKEN,
        project_id=project_id,
        watch_repo=watch_repo,
        num_commits=num_commits,
        average_range=average_range,
        average_min_count=average_min_count,
        debug=debug,
    )
