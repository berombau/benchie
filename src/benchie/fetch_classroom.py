import subprocess
from pathlib import Path

from loguru import logger


def main(solutions, task_id, force, subset):
    solutions = Path(solutions).resolve()
    solutions.mkdir(parents=True, exist_ok=True)

    # get list of submissions
    output = subprocess.check_output(
        [
            "gh",
            "classroom",
            "accepted-assignments",
            "-a",
            task_id,
            "--per-page",
            "100",
        ],
        cwd=solutions,
    )
    output = output.decode("utf-8").strip().split("\n")
    # take only the fifth line
    output = output[4:]
    output = [x.split() for x in output][:subset]
    # the repo url is the last element, first is the id
    logger.info(output)
    output = {x[0]: x[-1] for x in output}
    logger.info(output)
    for k, v in output.items():
        folder_name = "solution_" + k
        path = Path(solutions / folder_name).resolve()
        if not force and path.exists():
            logger.info(f"Updating {k}")
            subprocess.run(["git", "checkout", "main"], cwd=solutions / folder_name)
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
