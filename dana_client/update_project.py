import os
import shutil
import subprocess
from argparse import ArgumentParser

from git import Repo


def main():
    parser = ArgumentParser()

    parser.add_argument("--dana-url", type=str, required=True)
    parser.add_argument("--dana-dataset-id", type=str, required=True)
    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--watch-repo", type=str, required=True)
    parser.add_argument("--num-commits", type=int, default=10)

    args = parser.parse_args()

    dana_url = args.dana_url
    dana_dataset_id = args.dana_dataset_id
    project_id = args.project_id
    watch_repo = args.watch_repo
    num_commits = args.num_commits

    try:
        repo = Repo.clone_from(watch_repo, "watch_repo")
    except Exception:
        repo = Repo("watch_repo")

    commits = repo.iter_commits("main", max_count=num_commits)

    for commit in commits:
        build_hash = commit.hexsha
        build_abbrev_hash = commit.hexsha[:7]
        build_author_name = commit.author.name
        build_author_email = commit.author.email
        build_subject = commit.message
        build_url = f"{watch_repo}/commit/{commit}"
        build_id = str(commit.count())

        # checl if build exists
        out = subprocess.run(
            [
                "build-exists",
                "--dana-url",
                dana_url,
                "--project-id",
                project_id,
                "--build-id",
                build_id,
            ],
            capture_output=True,
        )

        if out.returncode == 0:
            print(f"Build {build_id} already exists, skipping...")
            continue

        # checkout the commit
        repo.git.checkout(build_hash)

        # install the watch_repo library
        subprocess.run(["pip", "install", "-e", "watch_repo"])

        for config_file in os.listdir("benchmarks"):
            config_name = os.path.splitext(config_file)[0]

            # skip _base_ config
            if config_name == "_base_":
                continue

            print(f"Running benchmarks for {config_name}")
            subprocess.run(
                [
                    "optimum-benchmark",
                    "--config-dir",
                    "benchmarks",
                    "--config-name",
                    config_name,
                    "--multirun",
                ]
            )

        subprocess.run(
            [
                "publish-build",
                "--build-folder",
                "experiments",
                "--dana-url",
                dana_url,
                "--dana-dataset-id",
                dana_dataset_id,
                "--project-id",
                project_id,
                "--build-id",
                build_id,
                "--build-hash",
                build_hash,
                "--build-abbrev-hash",
                build_abbrev_hash,
                "--build-author-name",
                build_author_name,
                "--build-author-email",
                build_author_email,
                "--build-subject",
                build_subject,
                "--build-url",
                build_url,
            ]
        )

        shutil.rmtree("experiments")


if __name__ == "__main__":
    main()
