import subprocess
import sys
from pathlib import Path

from loguru import logger

from benchie.utils import create_command


def _conclude_cmd(module_path):
    """
    Str of one-liner python code that remove the __pycache__ directories in the local path and PYTHONPATH.

    """
    return f'import pathlib; import shutil; [shutil.rmtree(p) for p in pathlib.Path("{module_path!s}").rglob("__pycache__")]'


def run_hyperfine_process_docker(docker_image, testfile, module_path, json_path, md_path, warmup, min_runs, names):
    output = json_path.parent.resolve()
    destination_root = "/submission"
    destination_output = f"{destination_root}/{output.name}"
    mount_output = f"--mount type=bind,source={output!s},destination={destination_output!s}"
    destination_module = f"{destination_root}/{module_path.name}"
    mount_module = f"--mount type=bind,source={module_path!s},destination={destination_module!s},readonly"
    src = "/submission/" + module_path.name
    json_path = destination_output + "/" + json_path.name
    md_path = destination_output + "/" + md_path.name
    executable = "'uv run --frozen --no-sync python'"
    subcommand = create_command(module_path, testfile)
    cmd_conclude = _conclude_cmd(src)
    logger.debug(f"Executable: {executable}")
    logger.debug(f"Subcommand: {subcommand}")
    logger.debug(f"Conclude command: {cmd_conclude}")
    command = f"""
        hyperfine --ignore-failure --export-json {json_path!s} --export-markdown {md_path!s} \
            -w {warmup} -m {min_runs} --shell {executable} --show-output --conclude \'{cmd_conclude}\' \
            {" ".join(["-n " + x for x in names])} \
            -L module {",".join(names)} \'{subcommand}\'
    """.strip()
    logger.info(f"Command: {command}")
    cmds = f"docker run -t --rm {mount_output} {mount_module} -e PYTHONPATH=$PYTHONPATH --entrypoint '/bin/bash' {docker_image} -c \"{command}\""
    return subprocess.run(cmds, shell=True, check=True, env={"PYTHONPATH": src})


def run_hyperfine_process(testfile, module_path, json_path, md_path, warmup, min_runs, names):
    subcommand = create_command(module_path, testfile)
    # subcommand = f"docker run -t --rm --mount type=bind,source=/Users/benjaminr/Documents/GitHub/benchmarks-2024/solutions/project/{{module}},destination=/submission,readonly --mount type=bind,source=/Users/benjaminr/Documents/GitHub/benchmarks-2024/data/project/{testfile.read_text().strip()},destination=/home/runner/data/Levine_13dim.fcs,readonly local_combio_project"
    executable = sys.executable
    # executable = "docker"
    cmd_conclude = _conclude_cmd(module_path)
    logger.debug(f"Executable: {executable}")
    logger.debug(f"Command: {subcommand}")
    logger.debug(f"Conclude command: {cmd_conclude}")
    command = f"""
        PYTHONPATH={module_path!s} hyperfine --ignore-failure --export-json {json_path!s} --export-markdown {md_path!s} \
            -w {warmup} -m {min_runs} --shell {executable} --show-output --conclude \'{cmd_conclude}\' \
            {" ".join(["-n " + x for x in names])} \
            -L module {",".join(names)} \'{subcommand}\'
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
    docker_image=None,
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
        if docker_image:
            results = run_hyperfine_process_docker(
                docker_image, testfile, module_path, json_path, md_path, warmup, min_runs, names
            )
        else:
            results = run_hyperfine_process(testfile, module_path, json_path, md_path, warmup, min_runs, names)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error while benchmarking: {e}")
        return
    return results
