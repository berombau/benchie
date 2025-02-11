import gc
import importlib
import subprocess
import sys
import tempfile
from pathlib import Path

import memray
from loguru import logger

from benchie.reporting import get_peak_memory_flamegraph


def create_memray_command(path, testfile, interpreter="python"):
    module = path.name.removesuffix(".py")
    fn_command = testfile.read_text()
    # command = f"""import {module}; {module}.global_alignment(\\'{str(testfile)}\\')"""
    command = f"""import {module}; {module}.{fn_command}
    """
    return command


def run_memray(output, solution, testfile, workdir, memray_executable=None, use_tracker=False, timeout=None):
    if memray_executable is None:
        memray_executable = (sys.executable + " -m memray").split()
    memray_bin = output / (solution.stem + "_memray.bin")
    # DANGER: arbitrary code import, only run on valid Dodona code!
    # set working dir to that of the solution file
    # os.chdir(solution.parent)
    memray_cmd = create_memray_command(solution, testfile)
    logger.debug(f"Created memray command: {memray_cmd}")
    if use_tracker:
        importlib.reload(memray)
        gc.collect()
        with memray.Tracker(
            file_name=memray_bin,
            native_traces=False,
            follow_fork=True,
            memory_interval_ms=10,
        ):
            try:
                exec(memray_cmd)
            except Exception as e:
                print(e)  # Output: Command 'exit 1' returned non-zero exit status 1.
    else:
        logger.debug(f"Running memray on {solution}")
        # create Python file in temp folder, run memray module on it
        temp_dir = Path(tempfile.mkdtemp())
        # copy over
        py_file = temp_dir / (solution.stem + "_memray.py")
        py_file.write_text(memray_cmd)
        try:
            subprocess.run(
                memray_executable + ["run", "-o", str(memray_bin), "--follow-fork", "-q", str(py_file)],
                check=True,
                timeout=timeout,
                env={"PYTHONPATH": str(solution.parent)},
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Memray failed with {e}")
            return None
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while memory profiling '{solution.stem}'")
            return None
    memray_flamegraph = output / (solution.stem + "_flamegraph.html")
    subprocess.run(
        memray_executable
        + [
            "flamegraph",
            "-o",
            str(memray_flamegraph),
            str(memray_bin),
        ]
    )
    # get peak memory
    peak_memory = get_peak_memory_flamegraph(memray_flamegraph)
    return peak_memory
