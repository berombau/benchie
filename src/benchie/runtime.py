import subprocess
import sys
from pathlib import Path

from loguru import logger


def run_once_docker(solution, testfile, timeout) -> None:
    src = "/submission/" + solution.name + "/src" if solution.is_dir() else "/submission"
    command = create_command(solution, testfile)
    logger.info(f"Command: {command}")
    cmds = f"docker run -t --rm --mount type=bind,source={solution!s},destination=/submission/{solution.name!s},readonly --entrypoint '/bin/bash' local_combio_project -c 'PYTHONPATH={src} python -c \"{command}\"'"
    logger.debug(f"Running command: {cmds}")
    subprocess.run(
        # [executable, "-c", command],
        cmds,
        check=True,
        timeout=timeout,
        # env=env,
        shell=True,
    )


def run_hyperfine_process_docker(testfile, module_path, json_path, md_path, warmup, min_runs, names):
    subcommand = "import {module}; {module}." + testfile.read_text()
    output = json_path.parent.resolve()
    # subcommand = f"docker run -t --rm --mount type=bind,source=/Users/benjaminr/Documents/GitHub/benchmarks-2024/solutions/project/{{module}},destination=/submission,readonly --mount type=bind,source=/Users/benjaminr/Documents/GitHub/benchmarks-2024/data/project/{testfile.read_text().strip()},destination=/home/runner/data/Levine_13dim.fcs,readonly local_combio_project"
    # executable = "docker"
    destination_root = "/submission"
    destination_output = f"{destination_root}/{output.name}"
    mount_output = f"--mount type=bind,source={output!s},destination={destination_output!s},readonly"
    destination_module = f"{destination_root}/{module_path.name}"
    mount_module = f"--mount type=bind,source={module_path!s},destination={destination_module!s},readonly"
    src = "/submission/" + module_path.name
    json_path = destination_output + "/" + json_path.name
    md_path = destination_output + "/" + md_path.name
    executable = "python"
    logger.debug(f"Executable: {executable}")
    logger.debug(f"Subcommand: {subcommand}")
    command = f"""
        hyperfine --ignore-failure --export-json {json_path!s} --export-markdown {md_path!s} \
            -w {warmup} -m {min_runs} --shell {executable} --show-output \
            {" ".join(["-n " + x for x in names])} \
            -L module {",".join(names)} '{subcommand}'"""
    logger.info(f"Command: {command}")
    cmds = f"docker run -t --rm {mount_output} {mount_module} --entrypoint '/bin/bash' local_combio_project -c 'PYTHONPATH={src} \"{command}\"'"
    return subprocess.run(cmds, shell=True, check=True)


def run_hyperfine_process(testfile, module_path, json_path, md_path, warmup, min_runs, names):
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
    return subprocess.run(command, shell=True, check=True)


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
    try:
        results = run_hyperfine_process(testfile, module_path, json_path, md_path, warmup, min_runs, names)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error while benchmarking: {e}")
        return
    return results
