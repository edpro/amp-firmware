from typing import List, Tuple, Optional
from math import sqrt

from tools.common.logger import LoggedError
from tools.common.screen import scr_print, Colors


def to_amp(v: float) -> float:
    return v * 2.0 * sqrt(2)


def from_amp(amp: float) -> float:
    return amp / 2.0 / sqrt(2)


def eabs(expected: float, actual: float) -> float:
    return abs(expected - actual)


def erel(expected: float, actual: float) -> float:
    if expected == 0 and actual == 0:
        return 0
    if expected == 0 or actual == 0:
        return 1
    return abs(expected - actual) / abs(expected)


def emax(expected: float, abs_err: float, rel_err: float):
    return abs_err + rel_err * abs(expected)


def abs_str(v: float):
    return f'{v:0.6f}'


def rel_str(v: float):
    return f'{v * 100:0.2f}%'


class TResult:
    actual: float
    expect: float
    abs_err: float
    rel_err: float
    max_diff: float

    def __init__(self, actual: float, expect: float, abs_err: float, rel_err: float):
        self.actual = actual
        self.expect = expect
        self.abs_err = eabs(actual, expect)
        self.rel_err = erel(actual, expect)
        self.max_diff = abs_err + rel_err * abs(expect)

    def abs_str(self):
        return f'{self.abs_err:0.6f}'

    def rel_str(self):
        if (self.rel_err == 0):
            return "-"
        else:
            return f'{self.rel_err * 100:0.1f}%'

    def expect_str(self):
        return f'{self.expect:0.6f}'

    def actual_str(self):
        return f'{self.actual:0.6f}'

    def rate_str(self):
        health_value = self.abs_err / self.max_diff
        return f'{round(health_value * 100)}%'

    def row_str(self, prefix: str):
        row = prefix
        row += f' | expect: {self.expect_str().rjust(9)}'
        row += f' | actual: {self.actual_str().rjust(9)}'
        row += f' | abs: {self.abs_str().rjust(8)}'
        row += f' | rel: {self.rel_str().rjust(6)}'
        row += f' | err: {self.rate_str().rjust(3)}'
        return row


class TestReporter:
    def __init__(self, tag: str, fail_fast: bool = False):
        self.tag = tag
        self.fail_fast = fail_fast
        self.records: List[Tuple[int, str]] = []
        self.success: bool = True
        scr_print(f'[{self.tag}] begin test', Colors.LIGHT_BLUE)

    def add_err_line(self, text: str):
        self.records.append((1, text))
        scr_print(f'[{self.tag}] {text}', Colors.LIGHT_RED)

    def expect(self, r: TResult):
        if r.abs_err < r.max_diff:
            return
        self.success = False
        self.add_err_line(f"FAILED: Value is not in range: {round(r.expect, 6)} ± {r.max_diff}")
        if self.fail_fast:
            raise LoggedError("Failed fast")

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
        scr_print(f'[{self.tag}] {text}', Colors.GREEN)

    def print_result(self):
        scr_print(f'[{self.tag}] result:', Colors.LIGHT_BLUE)
        for t, text in self.records:
            if t == 0:
                scr_print(f'| {text}', Colors.GRAY)
            elif t == 1:
                scr_print(f'| {text}', Colors.LIGHT_RED)
