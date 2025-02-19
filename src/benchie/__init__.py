import subprocess
import sys
import time
from pathlib import Path

from loguru import logger

from benchie.benchmark import benchmark
from benchie.fetch_submissions import refresh
from benchie.reporting import postprocess_output


def do_commit(cwd):
    """
    Commits the benchmark results to the repository.

    Args:
        cwd (str): The current working directory.

    Raises
    ------
        CalledProcessError: If any of the subprocess commands fail.

    """
    logger.info("Committing results")
    subprocess.run(["git", "add", "**/*benchmark.md"], check=True, cwd=cwd)
    subprocess.run(["pre-commit", "run", "--all-files"], check=False, cwd=cwd)
    subprocess.run(["git", "add", "**/*benchmark.md"], check=True, cwd=cwd)
    subprocess.run(["git", "commit", "-am", "benchmark solutions"], check=True, cwd=cwd)
    subprocess.run(["git", "pull", "--rebase"], check=True, cwd=cwd)
    subprocess.run(["git", "push"], check=True, cwd=cwd)


def main(
    output,
    data,
    force,
    commit,
    course_id,
    exercise_name,
    exercise_id,
    solutions,
    token,
    skip_fetch,
    skip_benchmark,
    subset,
    subset_data,
    disable_pretest,
    timeout,
    loop,
    loop_timeout,
    benchmark_options,
    docker_image,
    *args,
    **kwargs,
):
    """
    Main function for benchmarking and processing data.

    Args:
        output (str): Path to the output directory.
        data (str): Path to the data folder.
        force (bool): Flag indicating whether to force benchmarking even if there are no new submissions.
        commit (bool): Flag indicating whether to commit the changes.
        course_id (str): Course ID.
        exercise_name (str): Exercise name.
        exercise_id (str): Exercise ID.
        solutions (str): Path to the solutions directory.
        token (str): Path to the token location.
        skip_fetch (bool): Flag indicating whether to skip fetching new submissions.
        skip_benchmark (bool): Flag indicating whether to skip benchmarking.
        subset (int): Number of solutions to consider.
        subset_data (int): Number of data files to consider.
        disable_pretest (bool): Flag indicating whether to test the correctness of the solutions.
        timeout (float): Timeout value for benchmarking.
        loop (bool): Flag indicating whether to run the benchmark in an infinite loop.
        loop_timeout (float): Timeout value for the loop.
        benchmark_options (list[BenchmarkOption]): List of benchmarking options.
        docker_image (str): Docker image to use for benchmarking.

    Returns
    -------
        None
    """
    cwd: Path = Path.cwd().resolve()
    data = Path(data).resolve() / exercise_name
    if not data.exists():
        logger.error(f"Data folder {data} does not exist")
        return
    output = Path(output).resolve() / exercise_name
    output.mkdir(exist_ok=True, parents=True)
    solutions_path = Path(solutions).resolve() / exercise_name
    while True:
        if not skip_fetch:
            refreshed = refresh(
                # course id
                course_id,
                # exercise id
                exercise_id,
                # output directory
                solutions_path,
                # token location
                token,
            )
        else:
            refreshed = True
        logger.info(force)
        if force or refreshed:
            logger.info("New submissions or forced")
            # there is new data
            # benchmark(6, Path("reconstruction/J02459.1.6mers"), output=output)
            # benchmark(50, Path("reconstruction/J02459.1.50mers"), output=output)
            # make sure solutions are importable
            logger.debug(solutions_path)
            sys.path.append(str(solutions_path))

            # find folders or .py files
            all_solutions = [
                p for p in solutions_path.iterdir() if (p.is_dir() and p.name != "__pycache__") or p.suffix == ".py"
            ][:subset]
            logger.info(f"Found {len(all_solutions)} solutions.")
            valid_solutions = all_solutions

            data_paths: list[Path] = sorted(data.resolve().glob("data_*.py"))[:subset_data]
            if not data_paths:
                logger.info("No data to process")
                return
            for path in data_paths:
                if not valid_solutions:
                    logger.error("No valid solutions to benchmark.")
                    break
                assert path.exists(), f"Path {path} does not exist"
                logger.info(f"Testing on data {path.name}")
                output_folder_data = output / path.stem
                if not skip_benchmark:
                    valid_solutions = benchmark(
                        path,
                        subset=subset,
                        output=output_folder_data,
                        solutions=valid_solutions,
                        timeout=timeout,
                        disable_pretest=disable_pretest,
                        benchmark_options=benchmark_options,
                        docker_image=docker_image,
                    )
                logger.info("Postprocess")
                postprocess_output(path, output_folder_data)
                if commit:
                    logger.info("Committing")
                    do_commit(cwd)
                else:
                    logger.info("Not committing")
        else:
            # no new data
            logger.info("No new submissions. Not Benchmarking")
            if loop:
                logger.info(f"Sleeping for {loop_timeout} seconds.")
                time.sleep(loop_timeout)
        if not loop:
            break
