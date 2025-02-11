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

## Run as a student

### Example data

With the example data in this repository at `solutions/` and `data/` you can run the following command:

```bash
benchie run -S -e "example_sleep" --disable_pretest -b hyperfine -b memray_tracker
```

The output will be stored in `output/example_sleep/`.

### Custom data

Put different implementations at `solutions/{exercise_1}/{implementation_1}.py`.

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
