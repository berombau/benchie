from pathlib import Path

import benchie
from benchie.benchmark import BenchmarkOption


def test_sleep_hyperfine(sleep_solution, sleep_data, tmp_path):
    testfile = sleep_data / "data_01.py"
    solutions = list(sleep_solution.glob("*.py"))
    assert len(solutions) == 2
    assert tmp_path.exists()
    p = Path("test123").resolve()
    p.mkdir(exist_ok=True)
    output = benchie.benchmark(
        testfile=testfile,
        output=p,
        solutions=solutions,
        timeout=10,
        disable_pretest=False,
        benchmark_options=[BenchmarkOption.HYPERFINE.value],
    )
    assert len(output) == 2


def test_sleep_hyperfine_no_pycache(sleep_solution, sleep_data, tmp_path):
    testfile = sleep_data / "data_01.py"
    solutions = list(sleep_solution.glob("*.py"))
    assert len(solutions) == 2
    assert tmp_path.exists()
    p = Path("test123").resolve()
    p.mkdir(exist_ok=True)
    output = benchie.benchmark(
        testfile=testfile,
        output=p,
        solutions=solutions,
        timeout=10,
        disable_pretest=False,
        benchmark_options=[BenchmarkOption.HYPERFINE.value],
    )
    assert len(output) == 2
    # make sure __pychache__ is removed from solutions folder
    assert not (sleep_solution / "__pycache__").exists()
