import os
import shutil
import subprocess
import sys
import tempfile
from enum import Enum
from pathlib import Path

from loguru import logger

from benchie.memray import run_memray
from benchie.reporting import key_by_memory
from benchie.runtime import run_hyperfine_all


class BenchmarkOption(Enum):
    """Benchmarking options."""

    HYPERFINE = "hyperfine"
    SCALENE = "scalene"
    MEMRAY_TRACKER = "memray_tracker"
    MEMRAY_IMPORTS = "memray_imports"


def create_command(path, testfile, interpreter="python"):
    """Create a command to execute a test file using a given path and interpreter."""
    if path.is_dir():
        assert (path / "src").exists(), f"Source folder {path / 'src'} does not exist"
        module = list((path / "src").iterdir())[0].name
    else:
        module = path.name.removesuffix(".py")
    fn_command = testfile.read_text()
    command = f"""import {module}; {module}.{fn_command}
    """
    return command


def prep_workdir(data_folder, chdir=True):
    tmp = Path(tempfile.mkdtemp())
    # copy all files from data folder to tmp, except .py files
    for path in data_folder.glob("*"):
        if path.suffix != ".py":
            shutil.copy(path, tmp)
    if chdir:
        os.chdir(tmp)
    return tmp


def run_once(solution, testfile, timeout) -> None:
    executable = sys.executable
    if solution.is_dir():
        src = solution / "src"
        if not src.exists():
            logger.error(f"Source folder {src} does not exist")
            raise FileNotFoundError(f"Source folder {src} does not exist")
        env = {"PYTHONPATH": str(src)}
    else:
        env = {"PYTHONPATH": str(solution.parent)}
    command = create_command(solution, testfile)
    logger.info(f"Command: {command}")
    # cmds = f"docker run -it --rm --mount type=bind,source={solution!s},destination=/submission,readonly local_combio_project"
    # logger.debug(f"Running command: {cmds}")
    subprocess.run(
        [executable, "-c", command],
        # cmds,
        check=True,
        timeout=timeout,
        env=env,
        # shell=True,
    )


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


def benchmark(
    testfile,
    output,
    solutions,
    timeout,
    disable_pretest,
    benchmark_options: list[BenchmarkOption],
    subset=None,
):
    """
    Perform benchmarking on submissions.

    Args:
        testfile (Path): Path to the test file.
        subset (str): Subset of the test file to use.
        output (Path): Path to the output directory.
        solutions (List[Path]): List of paths to the solutions.
        timeout (int): Timeout value in seconds.

    Returns
    -------
        List[Path]: List of correct solutions.

    """
    logger.info("Benchmarking submissions")
    if output.exists():
        # remove everything in the output directory, except the .md files
        for path in output.glob("*"):
            if path.suffix != ".md":
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
    output.mkdir(exist_ok=True)

    testfile = testfile.resolve()
    prep_workdir(testfile.parent)

    if not disable_pretest:
        # test solution correctness and report errors
        logger.info("Testing correctness.")
        all_correct_solutions = []
        for solution in solutions:
            try:
                run_once(solution, testfile, timeout)
                # code = with_timeout(timeout, action='timeout')(exec)(command)
                # if code == 'timeout':
                #     logger.error(f"Timeout while testing '{solution.stem}'")
                #     continue
                # exec(command)
            except FileNotFoundError:
                logger.error(f"File not found while testing '{solution.stem}'")
                continue
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout while testing '{solution.stem}'")
                continue
            except subprocess.CalledProcessError as e:
                logger.error(f"Error while testing '{solution.stem}'; {e}")
                continue
            all_correct_solutions.append(solution)
        logger.info(f"Correct solutions: {len(all_correct_solutions)}")
    else:
        all_correct_solutions = solutions

    if BenchmarkOption.HYPERFINE.value in benchmark_options:
        run_hyperfine_all(output, all_correct_solutions, testfile, subset=subset)

    # prepare for memory profiling
    n_memory_profiles = 3

    for path in all_correct_solutions:
        # change work dir to the solutions path
        if BenchmarkOption.MEMRAY_TRACKER.value in benchmark_options:
            peaks = []
            for i in range(n_memory_profiles):
                logger.debug(f"Running memray on {path}, {i}")
                workdir = prep_workdir(testfile.parent)
                i_output = output / f"memray_{i}"
                i_output.mkdir(exist_ok=True)
                memray_peak = run_memray(i_output, path, testfile, workdir, use_tracker=True, timeout=timeout)
                logger.debug(f"Peak memory usage: {memray_peak}")
                peaks.append(memray_peak)
            # get median peak memory usage, with support for KiB and MiB
            median_peak = sorted(peaks, key=lambda x: key_by_memory(x))[len(peaks) // 2]
            logger.info(f"Median peak memory usage: {median_peak}")
            # write median peak memory usage to file
            output_peak = output / f"{path.stem}_memray.txt"
            output_peak.write_text(str(median_peak))
        if BenchmarkOption.MEMRAY_IMPORTS.value in benchmark_options:
            logger.debug(f"Running memray on {path}")
            workdir = prep_workdir(testfile.parent)
            i_output = output / "memray_imports"
            i_output.mkdir(exist_ok=True)
            memray_peak = run_memray(i_output, path, testfile, workdir, use_tracker=False, timeout=timeout)
            logger.debug(f"Peak memory usage: {memray_peak}")
            # write median peak memory usage to file
            output_peak = output / f"{path.stem}_memray_imports.txt"
            output_peak.write_text(str(memray_peak))
        if BenchmarkOption.SCALENE.value in benchmark_options:
            from benchie.scalene import run_scalene

            peaks = []
            for i in range(n_memory_profiles):
                i_output = output / f"memory_{i}"
                i_output.mkdir(exist_ok=True)
                run_scalene(i_output, path, testfile)
    return all_correct_solutions
