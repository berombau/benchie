import subprocess
from pathlib import Path

from loguru import logger


def main(solutions, task_id, force, subset):
    # import json
    # from pathlib import Path
    # import requests
    # from loguru import logger
    # from benchie.fetch_submissions import fetch_correct, write_submissions
    # from benchie.fetch_subgit import fetch_subgit_main
    # from benchie.main import main
    solutions = Path(solutions).resolve()
    solutions.mkdir(parents=True, exist_ok=True)

    # get list of submissions
    output = subprocess.check_output(
        [
            "ssh",
            "git@subgit.ugent.be",
            "students",
            task_id,
            "-l",
        ],
        cwd=solutions,
    )
    output = output.decode("utf-8").strip().split("\n")
    output = [x.split() for x in output][:subset]
    output = {x[0]: x[-1] for x in output}
    logger.info(output)

    for k, v in output.items():
        folder_name = "solution_" + k
        path = Path(solutions / folder_name).resolve()
        if not force and path.exists():
            logger.info(f"Updating {k}")
            subprocess.run(["git", "checkout", "master"], cwd=solutions / folder_name)
            subprocess.run(
                [
                    "git",
                    "pull",
                ],
                cwd=solutions / folder_name,
            )
        else:
            # remove dir if it exists
            if path.exists():
                output = subprocess.run(
                    [
                        "rm",
                        "-rf",
                        folder_name,
                    ],
                    cwd=solutions,
                )
            logger.info(f"Cloning {k}")
            output = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    v,
                    folder_name,
                ],
                cwd=solutions,
            )
