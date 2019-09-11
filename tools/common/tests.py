from typing import List, Tuple, Optional
from tools.common.screen import print_color, Colors


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

    def expect_abs_rel(self, expected: float, actual: float, abs: float, rel: float):
        ea = eabs(expected, actual)
        er = erel(expected, actual)
        if ea <= abs or er <= rel:
            return

        if ea > abs:
            self.success = False
            self.add_err_line(f"Error: absolute error ({ea:0.6f}) must be less then {abs:0.6f}")
            self.add_err_line(f"    expected: {expected:0.6f}")
            self.add_err_line(f"    actual:   {actual:0.6f}")
        else:
            self.success = False
            self.add_err_line(f"Error: relative error ({er:0.6f}) must be less then {rel:0.6f}")
            self.add_err_line(f"    expected: {expected:0.6f}")
            self.add_err_line(f"    actual:   {actual:0.6f}")

    def expect_abs(self, actual: float, expected: float, err: Optional[float]):
        if (err is None):
            return
        e = eabs(expected, actual)
        if e <= err:
            return
        self.success = False
        self.add_err_line(f"Error: absolute error ({e:0.6f}) must be less then {err:0.6f}")
        self.add_err_line(f"    expected: {expected:0.6f}")
        self.add_err_line(f"    actual:   {actual:0.6f}")

    def expect_rel(self, actual: float, expected: float, err: Optional[float]):
        if (err is None):
            return
        e = erel(expected, actual)
        if e <= err:
            return
        self.success = False
        self.add_err_line(f"Error: relative error ({e:0.6f}) must be less then {err:0.6f}")
        self.add_err_line(f"    expected: {expected:0.6f}")
        self.add_err_line(f"    actual:   {actual:0.6f}")

    def expect_int(self, actual: int, expected: int, msg: str):
        if actual == expected:
            return
        self.success = False
        self.add_err_line(f'Error: {msg}')
        self.add_err_line(f"    expected: {expected}")
        self.add_err_line(f"    actual:   {actual}")

    def trace(self, text: str):
        self.records.append((0, text))
        print_color(f'[{self.tag}] {text}', Colors.GREEN)

    def print_result(self):
        print_color(f'[{self.tag}] result:', Colors.LIGHT_BLUE)
        for t, text in self.records:
            if t == 0:
                print_color(f'[{self.tag}] {text}', Colors.GRAY)
            elif t == 1:
                print_color(f'[{self.tag}] {text}', Colors.LIGHT_RED)
