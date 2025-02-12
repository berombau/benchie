from benchie.benchmark import run_once_docker
from benchie.runtime import run_hyperfine_process_docker


def test_run_once_docker(sleep_solution, sleep_data):
    testfile = sleep_data / "data_01.py"
    solution = next(iter(sleep_solution.glob("*.py")))
    run_once_docker(solution, testfile, 10)


def test_run_hyperfine_process_docker(sleep_solution, sleep_data, tmp_path):
    testfile = sleep_data / "data_01.py"
    solution = next(iter(sleep_solution.glob("*.py")))
    run_hyperfine_process_docker(
        testfile, solution.parent, tmp_path / "test.json", tmp_path / "test.md", 1, 3, ["solution"]
    )
