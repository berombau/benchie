from pathlib import Path

import pytest


@pytest.fixture
def docker_image():
    return "local_combio_project"


@pytest.fixture
def project_root():
    p = Path(__file__).parent.parent.resolve()
    assert p.exists()
    return p


@pytest.fixture
def solutions(project_root):
    p = project_root / "solutions"
    assert p.exists()
    return p


@pytest.fixture
def data(project_root):
    p = project_root / "data"
    assert p.exists()
    return p


@pytest.fixture
def output(project_root):
    p = project_root / "output"
    assert p.exists()
    return p


@pytest.fixture
def testfile(project_root):
    p = project_root / "testfile"
    assert p.exists()
    return p


@pytest.fixture
def sleep_solution(solutions):
    p = solutions / "example_sleep"
    assert p.exists()
    return p


@pytest.fixture
def sleep_data(data):
    p = data / "example_sleep"
    assert p.exists()
    return p


@pytest.fixture
def bio_solution(solutions):
    p = solutions / "example_bio"
    assert p.exists()
    return p


@pytest.fixture
def bio_data(data):
    p = data / "example_bio"
    assert p.exists()
    return p
