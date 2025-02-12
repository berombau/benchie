# benchie

[![Release](https://img.shields.io/github/v/release/berombau/benchie)](https://img.shields.io/github/v/release/berombau/benchie)
[![Build status](https://img.shields.io/github/actions/workflow/status/berombau/benchie/main.yml?branch=main)](https://github.com/berombau/benchie/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/berombau/benchie/branch/main/graph/badge.svg)](https://codecov.io/gh/berombau/benchie)
[![Commit activity](https://img.shields.io/github/commit-activity/m/berombau/benchie)](https://img.shields.io/github/commit-activity/m/berombau/benchie)
[![License](https://img.shields.io/github/license/berombau/benchie)](https://img.shields.io/github/license/berombau/benchie)

A tool for automating benchmarks of programming assignments.

- **Github repository**: <https://github.com/berombau/benchie/>
- **Documentation** <https://berombau.github.io/benchie/>

## Installation

Install [uv](https://docs.astral.sh/uv/getting-started/installation/).

You can run the tool without installation using the following command:

```
uvx benchie --help
```

To install the tool in an environment, you can run:

```bash
uv venv
uv pip install benchie
```

## Current support

Fetching assignments works for [Dodona](https://docs.dodona.be) and [subgit](https://subgit.ugent.be/) submissions.

Currently supported benchmarking:

- execution time ([hyperfine](https://github.com/sharkdp/hyperfine) with or without a Docker container)
- peak memory usage ([memray](https://github.com/bloomberg/memray))
  - (with_imports) uses `python -m memray` and includes the memory usage of the imports
  - (with_tracker) uses a median of 3 executions with `memray.Tracker`, which would not show the memory usage of the imports

## Planned support

- [ ] Docker support for memray
- [ ] Support for GitHub Classroom

## Run as a student

### Example data

With the example data in this repository at `solutions/` and `data/` you can run the following command:

```bash
benchie run -S -e "example_sleep" -b hyperfine -b memray_tracker
```

The output will be stored in `output/example_sleep/`.

### Run within a Docker container

First build and tag a local image with a specific name. Here we use the Dockerfile in the repository root:

```bash
docker build -t local_combio_project .
```

Then we can run a container from this image with the following command:

```bash
benchie run -S -e "example_sleep" -b hyperfine --docker_image local_combio_project
```

Memray is currently not yet supported in Docker containers.

### Custom data

Put different implementations at `solutions/{exercise_1}/{implementation_1}.py`. Note that it's best to use double quotes '""' instead of single quotes "''" because of some current string parsing limitations.

Run the benchmark with disabled fetching of Dodona submissions and only the first 3 datasets:

```
benchie run -S -e "{exercise_1}" --subset_data 3
```

Output will be stored in `output/{exercise_1}`.

## Run as a teacher

Fetch token from Dodona user profile and store as `token` file.

### Setup recurrent job

- Use [deploy keys](https://docs.github.com/en/developers/overview/managing-deploy-keys)
- Use git instead of https as git origin remote URL
- setup cron job
- copy conda init lines from ~/.bashrc to ~/.bashrc_conda

Use `crontab -e` to add a cron job (edit the repo path):

```
SHELL=/bin/bash
BASH_ENV=~/.bashrc_conda
0 * * * * conda activate combio_benchmark_2024; timeout --signal=KILL 1h benchie run -e "global_alignment" -fC >> ~/combio_benchmark_job.log 2>&1
```

---

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
