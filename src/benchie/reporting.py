import json
import re

from loguru import logger


def get_peak_memory_flamegraph(p):
    tree = p.read_text()
    regex = r"Peak memory usage: ([^<]+)<br>"
    match = re.search(regex, tree)
    peak = match.group(1) if match else 0
    return peak


def get_all_peak_memory(output):
    with_imports = {}
    with_tracker = {}
    for p in output.glob("*_memray_imports.txt"):
        name = p.stem.removesuffix("_memray_imports")
        with_imports[name] = p.read_text()
    for p in output.glob("*_memray.txt"):
        name = p.stem.removesuffix("_memray")
        with_tracker[name] = p.read_text()
    return with_imports, with_tracker


def get_all_peak_memory_flamegraph(output):
    d = {}
    for p in output.glob("*_flamegraph.html"):
        # Get contents like "Peak memory usage: 5.2 MiB<br>"
        peak = get_peak_memory_flamegraph(p)
        name = p.stem.split("_")[1]
        d[name] = peak
    return d


def get_peak_memory_tree(output):
    d = {}
    for p in output.glob("*_tree.txt"):
        name = p.stem.split("_")[1]
        tree = p.read_text()
        regex = r"Peak memory size: ([A-Za-z.0-9]+)"
        match = re.search(regex, tree)
        peak = match.group(1) if match else 0
        d[name] = peak
    return d


def key_by_memory(s):
    """_summary_

    :param s: _description_
    :return: _description_
    >>> key_by_memory('1.0 MB')
    1.0
    >>> key_by_memory('1.0 GB')
    1000.0
    """
    if s.endswith("KB") or s.endswith("KiB"):
        return float(s[:-3]) / 1000
    elif s.endswith("MB") or s.endswith("MiB"):
        return float(s[:-3])
    elif s.endswith("GB") or s.endswith("GiB"):
        return float(s[:-3]) * 1000
    else:
        # e.g. None
        return float("inf")


def make_relative(d):
    """_summary_

    :param d: _description_
    :return: _description_
    >>> make_relative({'a': '1.0 MB', 'b': '2.0 MB'})
    {'a': 0, 'b': 1}
    >>> make_relative({'a': '1.0 MB', 'b': '1.0 MB'})
    {'a': 0, 'b': 1}
    >>> make_relative({'a': '1.0 GB', 'b': '2.0 KB'})
    {'b': 0, 'a': 1}
    """
    sort_d = sorted(d.items(), key=lambda x: key_by_memory(x[1]))
    d_relative = {k: i for i, (k, _) in enumerate(sort_d)}
    return d_relative


def create_table(with_imports, with_tracker, timings=None):
    r"""
    Expected output:

    | Command | Mean [s] | Min [s] | Max [s] | Rank |
    |:---|---:|---:|---:|---:|
    | `13309298` | 4.500 ± 0.036 | 4.474 | 4.541 | 1.00 |
    | `13309297` | 4.515 ± 0.116 | 4.445 | 4.648 | 1.00 ± 0.03 |

    >>> create_table({'13309298': '1.0 MB'})
    ' | Command | Peak memory | Rank | \n | :--- | ---: | ---: | \n | `13309298` |  |  |  | 1.0 MB | 0 | '
    >>> create_table({'13309298': '1.0 MB'}, {'results': [{'command': '13309298', 'mean': 4.5, 'stddev': 0.036, 'min': 4.474, 'max': 4.541}]})
    ' | Command | Mean [s] | Min [s] | Max [s] | Peak memory | Rank | \n | :--- | ---: | ---: | ---: | ---: | ---: | \n | `13309298` | 4.500 ± 0.036 | 4.474 | 4.541 | 1.0 MB | 0 | '
    """
    output = []
    d = " | "

    if timings is None:
        header = ["Command"]
        if with_imports:
            header.append("(with_imports) Peak memory")
        if with_tracker:
            header.append("(with_tracker) Median peak memory")
        header.append("Rank")
        output.append(d + d.join(header) + d)
        output.append(d + d.join([":---", *["---:" for _ in range(len(header) - 1)]]) + d)

        relative_peaks = make_relative(with_imports or with_tracker)
        for k in relative_peaks:
            columns = [f"`{k}`"]
            if with_imports:
                columns.append(with_imports[k])
            if with_tracker:
                columns.append(with_tracker[k])
            columns.append(str(relative_peaks[k]))
            output.append(d + d.join([str(c) for c in columns]) + d)
    else:
        header = ["Command", "Mean [s]", "Min [s]", "Max [s]"]
        if with_imports:
            header.append("(with_imports) Peak memory")
        if with_tracker:
            header.append("(with_tracker) Median peak memory")
        header.append("Rank")
        output.append(d + d.join(header) + d)
        output.append(d + d.join([":---", *["---:" for _ in range(len(header) - 1)]]) + d)
        d_relative = make_relative(with_imports or with_tracker)
        for c in timings["results"]:
            name = c["command"]
            columns = [
                f"{x:.3f}" if isinstance(x, float) else str(x)
                for x in [
                    f"`{name}`",
                    # mean + stdev,
                    f"{c['mean']:.3f} ± {c['stddev']:.3f}",
                    # min,
                    c["min"],
                    # max,
                    c["max"],
                ]
            ]
            if with_imports:
                columns.append(with_imports[name])
            if with_tracker:
                columns.append(with_tracker[name])
            columns.append(str(d_relative[name]))
            output.append(d + d.join(columns) + d)
    return "\n".join(output)


def postprocess_output(path, output):
    name = path.stem
    any_output = False

    # add hyperfine output
    timings = None
    json_path = output / (name + "_benchmark.json")
    if json_path.exists():
        any_output = True
        timings = json.loads(json_path.read_text(encoding="utf8"))

    ## add memray output
    with_imports, with_tracker = get_all_peak_memory(output)
    if with_imports or with_tracker:
        any_output = True
        # run only if memory profiling present
        table = create_table(with_imports, with_tracker, timings=timings)
        table_path = output / (name + "_memory_benchmark.md")
        table_path.write_text(table)

    if not any_output:
        logger.info("No output to process")
        return


if __name__ == "__main__":
    import doctest

    doctest.testmod()
