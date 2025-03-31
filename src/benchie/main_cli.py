import click
from loguru import logger

from benchie import main as run_main
from benchie.benchmark import BenchmarkOption
from benchie.fetch_classroom import main as fetch_classroom_main
from benchie.fetch_subgit import main as fetch_subgit_main
from benchie.fetch_submissions import main as fetch_main


@click.group()
def main_cli():
    pass


@click.command()
@click.option(
    "-o",
    "--output",
    default="output",
    type=click.Path(),
    help="Output folder to write benchmark result files.",
)
@click.option(
    "-d",
    "--data",
    default="data",
    type=click.Path(),
    help="Data folder to read input files from.",
)
@click.option(
    "-s",
    "--solutions",
    default="solutions",
    type=click.Path(),
    help="Folder to fetch and read submissions.",
)
@click.option("-c", "--course_id", default="3363", help="Dodona course id.")
@click.option("-e", "--exercise_name", default="global_alignment", help="Exercise name.")
@click.option("-E", "--exercise_id", default="1076300121", help="Dodona exercise id.")
@click.option("-t", "--token", default="token", type=click.Path(), help="Dodona token location.")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Run even though there are no new submissions.",
)
@click.option("-S", "--skip_fetch", is_flag=True, help="Skip fetching new submissions.")
@click.option("--skip_benchmark", is_flag=True, help="Skip benchmark.")
@click.option("-C", "--commit", is_flag=True, help="Commit end results using git.")
@click.option(
    "-N",
    "--subset",
    default=None,
    type=int,
    help="Number of submissions to subset.",
)
@click.option(
    "--subset_data",
    default=None,
    type=int,
    help="Number of data files to subset.",
)
@click.option("-T", "--timeout", default=30, type=int, help="Timeout for benchmarking.")
@click.option(
    "--disable_pretest",
    is_flag=True,
    help="Disable the correctness test of the solutions before benchmarking.",
)
@click.option("-L", "--loop", is_flag=True, help="Run benchmark in infinite loop.")
@click.option("--loop_timeout", default=10 * 60, type=int, help="Timeout for the loop in seconds.")
@click.option(
    "-b",
    "--benchmark_options",
    multiple=True,
    default=[],
    type=click.Choice([option.value for option in BenchmarkOption]),
    help="Benchmarking options.",
)
@click.option(
    "--docker_image",
    default=None,
    type=str,
    help="Docker image to use for benchmarking.",
)
def run(
    output,
    data,
    solutions,
    course_id,
    exercise_name,
    exercise_id,
    token,
    force,
    skip_fetch,
    skip_benchmark,
    commit,
    subset,
    subset_data,
    disable_pretest,
    loop,
    loop_timeout,
    timeout,
    benchmark_options,
    docker_image,
):
    args = {
        "output": output,
        "data": data,
        "solutions": solutions,
        "course_id": course_id,
        "exercise_name": exercise_name,
        "exercise_id": exercise_id,
        "token": token,
        "force": force,
        "skip_fetch": skip_fetch,
        "skip_benchmark": skip_benchmark,
        "commit": commit,
        "subset": subset,
        "subset_data": subset_data,
        "disable_pretest": disable_pretest,
        "timeout": timeout,
        "loop": loop,
        "loop_timeout": loop_timeout,
        "benchmark_options": benchmark_options,
        "docker_image": docker_image,
    }
    logger.info(args)
    run_main(**args)


@click.command()
@click.option(
    "-s",
    "--solutions",
    default="solutions/alignment",
    type=click.Path(),
    help="Folder to fetch and read submissions.",
)
@click.option("-c", "--course_id", default="3363", help="Dodona course id.")
@click.option("-e", "--exercise_id", default="1315421652", help="Dodona exercise id.")
@click.option("-f", "--force", is_flag=True, help="Force write all submissions.")
def fetch(solutions, course_id, exercise_id, force):
    args = {"solutions": solutions, "course_id": course_id, "exercise_id": exercise_id, "force": force}
    logger.info(args)
    fetch_main(**args)


@click.command()
@click.option(
    "-s",
    "--solutions",
    default="solutions/project",
    type=click.Path(),
    help="Folder to fetch and read submissions.",
)
@click.option("-i", "--task_id", default="2023-2024/combio/project", help="Subgit task id.")
@click.option("-f", "--force", is_flag=True, help="Force write all submissions.")
@click.option("-N", "--subset", default=None, type=int, help="Number of submissions to subset.")
def fetch_subgit(solutions, task_id, force, subset):
    args = {"solutions": solutions, "task_id": task_id, "force": force, "subset": subset}
    logger.info(args)
    fetch_subgit_main(**args)


@click.command()
@click.option(
    "-s",
    "--solutions",
    type=click.Path(),
    help="Folder to fetch and read submissions.",
)
@click.option("-i", "--task_id", type=str, help="Classroom assignment id.")
@click.option("-f", "--force", is_flag=True, help="Force write all submissions.")
@click.option("-N", "--subset", default=None, type=int, help="Number of submissions to subset.")
def fetch_classroom(solutions, task_id, force, subset):
    args = {"solutions": solutions, "task_id": task_id, "force": force, "subset": subset}
    logger.info(args)
    fetch_classroom_main(**args)


main_cli.add_command(run)
main_cli.add_command(fetch)
main_cli.add_command(fetch_subgit)
main_cli.add_command(fetch_classroom)

if __name__ == "__main__":
    main_cli()
