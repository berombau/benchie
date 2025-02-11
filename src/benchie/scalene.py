import subprocess
from pathlib import Path

from loguru import logger
from scalene import scalene_profiler
from scalene.scalene_parseargs import ScaleneParseArgs


def import_solution(solution):
    try:
        mod = __import__(solution)
    except ImportError as e:
        logger.info(f"Import failed for: {solution}; {e}")
        mod = None
    return mod


def create_scalene_command(path, testfile, interpreter="python"):
    module = path.name.removesuffix(".py")
    fn_command = testfile.read_text()
    # command = f"""import {module}; {module}.global_alignment(\\'{str(testfile)}\\')"""
    command = f"""import {module}; {module}.{fn_command}
    """
    return command


def run_scalene_directly(output, solution, testfile):
    output / (solution.stem + "_scalene.bin")
    module = solution.name.removesuffix(".py")
    # DANGER: arbitrary code import, only run on valid Dodona code!
    mod = import_solution(module)

    (
        args,
        left,
    ) = ScaleneParseArgs.parse_args()
    scalene_profiler.Scalene.set_initialized()
    scalene_profiler.Scalene.run_profiler(args, left)
    scalene_profiler.Scalene.set_initialized()
    # Turn profiling on
    scalene_profiler.start()
    try:
        dm = mod.DistanceMatrix.loadtxt(testfile)
        dm.neighbour_joining()
    except ValueError as e:
        print(e)  # Output: Command 'exit 1' returned non-zero exit status 1.

    # Turn profiling off
    scalene_profiler.stop()
    # scalene_profiler.
    # use async Popen, don't wait for return
    # with open(output / (solution.stem + '_summary.txt'), "w") as f:
    #     subprocess.Popen(['memray', 'summary', str(output_path)], stdout=f)
    # with open(output / (solution.stem + '_tree.txt'), "w") as f:
    #     subprocess.Popen(['memray', 'tree', str(output_path)], stdout=f)
    # with open(output / (solution.stem + '_stats.txt'), "w") as f:
    #     subprocess.Popen(['memray', 'stats', str(output_path)], stdout=f)
    # subprocess.Popen(['memray', 'flamegraph', '-o', output / (solution.stem + '_flamgraph.html'), str(output_path)])
    # subprocess.Popen(['memray', 'table', '-o', output / (solution.stem + '_table.html'), str(output_path)])


def run_scalene(output_folder, solution, testfile, format="json"):
    output_path = output_folder / ((solution.stem) + "_scalene." + format)
    # all_solutions = list(solutions_path.glob("*.py"))
    # names = [x.stem.split('_')[1] for x in all_solutions]
    # command = create_command_scalene(solution, testfile)
    # assert len(commands) > 1
    runner = Path("data/global_alignment").resolve() / "scalene_runner.py"
    logger.info("Benchmarking")

    command = f"""
        cd {solution.parent!s};
        scalene --cpu --mem --{format} --profile-only {solution!s} --off {runner!s} --- {solution!s} {testfile!s} > {output_path!s}
    """
    logger.info(f"Command {command}")
    try:
        results = subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error while benchmarking: {e}")
        return
    return results
