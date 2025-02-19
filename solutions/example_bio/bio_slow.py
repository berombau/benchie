import time

from Bio.Seq import Seq


def example_bio(n: int, _: Seq | None = None):
    time.sleep(n + 0.1)
