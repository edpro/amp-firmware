from typing import List, Tuple, Optional
from math import sqrt

from tools.common.screen import print_color, Colors


def to_amp(v: float) -> float:
    return v * 2.0 * sqrt(2)


def from_amp(amp: float) -> float:
    return amp / 2.0 / sqrt(2)


def eabs(expected: float, actual: float) -> float:
    return abs(expected - actual)


def erel(expected: float, actual: float) -> float:
    if expected == 0 and actual == 0:
        return 0
    return abs(expected - actual) / max(abs(expected), abs(actual))


def abs_str(v: Optional[float]):
    if (v is None):
        return "None"
    else:
        return f'{v:0.6f}'


def rel_str(v: Optional[float]):
    if (v is None):
        return "None"
    else:
        return f'{v * 100:0.2f}%'


class TestReporter:
    def __init__(self, tag: str):
        self.tag = tag
        self.records: List[Tuple[int, str]] = []
        self.success: bool = True
        print_color(f'[{self.tag}] begin test', Colors.LIGHT_BLUE)

    def add_err_line(self, text: str):
        self.records.append((1, text))
        print_color(f'[{self.tag}] {text}', Colors.LIGHT_RED)

    def expect_abs(self, actual: float, expect: float, err: Optional[float]):
        if (err is None):
            return
        e = eabs(expect, actual)
        if e <= err:
            return
        self.success = False
        self.add_err_line(f"FAILED: Absolute error {round(e, 6)} > {err}")

    def expect_rel(self, actual: float, expect: float, err: Optional[float]):
        if (err is None):
            return
        e = erel(expect, actual)
        if e <= err:
            return
        self.success = False
        self.add_err_line(f"FAILED: Relative error {round(e, 6)} > {err}")

    def expect_int(self, actual: int, expect: int, msg: str):
        if actual == expect:
            return
        self.success = False
        self.add_err_line(f'FAILED: {msg}')
        self.add_err_line(f"\texpect: {expect}")
        self.add_err_line(f"\tactual: {actual}")

    def trace(self, text: str):
        self.records.append((0, text))
        print_color(f'[{self.tag}] {text}', Colors.GREEN)

    def print_result(self):
        print_color(f'[{self.tag}] result:', Colors.LIGHT_BLUE)
        for t, text in self.records:
            if t == 0:
                print_color(f'| {text}', Colors.GRAY)
            elif t == 1:
                print_color(f'| {text}', Colors.LIGHT_RED)
