import subprocess
import sys
from pathlib import Path

from loguru import logger


def run_hyperfine_all(
    output,
    all_correct_solutions,
    testfile,
    json_path=None,
    md_path=None,
    warmup=1,
    min_runs=3,
    subset=None,
):
    name = testfile.stem
    json_path = Path(json_path or output / f"{name}_benchmark.json")
    md_path = Path(md_path or output / f"{name}_benchmark.md")
    logger.info(f"Found {len(all_correct_solutions)} solutions to benchmark.")
    if len(all_correct_solutions) == 0:
        logger.error("No valid solutions to benchmark.")
        return
    module_path = all_correct_solutions[0].parent
    names = [x.stem for x in all_correct_solutions]

    # DANGER: arbitrary code run, only run on valid Dodona code!

    subcommand = "import {module}; {module}." + testfile.read_text()
    # subcommand = f"docker run -t --rm --mount type=bind,source=/Users/benjaminr/Documents/GitHub/benchmarks-2024/solutions/project/{{module}},destination=/submission,readonly --mount type=bind,source=/Users/benjaminr/Documents/GitHub/benchmarks-2024/data/project/{testfile.read_text().strip()},destination=/home/runner/data/Levine_13dim.fcs,readonly local_combio_project"
    executable = sys.executable
    # executable = "docker"
    logger.debug(f"Executable: {executable}")
    logger.debug(f"Command: {subcommand}")
    command = f"""
        PYTHONPATH={module_path!s} hyperfine --ignore-failure --export-json {json_path!s} --export-markdown {md_path!s} \
            -w {warmup} -m {min_runs} --shell {executable} --show-output \
            {" ".join(["-n " + x for x in names])} \
            -L module {",".join(names)} '{subcommand}'
    """
    logger.info(f"Command {command}")
    try:
        results = subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error while benchmarking: {e}")
        return
    return results
