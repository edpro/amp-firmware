from typing import List, Tuple
from tools.common.screen import print_color, Colors


def eabs(expected: float, actual: float) -> float:
    return abs(expected - actual)


def erel(expected: float, actual: float) -> float:
    if expected == 0 and actual == 0:
        return 0
    return abs(expected - actual) / max(abs(expected), abs(actual))


class TestReporter:
    def __init__(self, tag: str):
        self.tag = tag
        self.records: List[Tuple[int, str]] = []
        self.success: bool = True
        print_color(f'[{self.tag}] begin test', Colors.LIGHT_BLUE)

    def add_err_line(self, text):
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

    def expect_abs(self, expected: float, actual: float, err: float):
        e = eabs(expected, actual)
        if e <= err:
            return
        self.success = False
        self.add_err_line(f"Error: absolute error ({e:0.6f}) must be less then {err:0.6f}")
        self.add_err_line(f"    expected: {expected:0.6f}")
        self.add_err_line(f"    actual:   {actual:0.6f}")

    def expect_rel(self, expected: float, actual: float, err: float):
        e = erel(expected, actual)
        if e <= err:
            return
        self.success = False
        self.add_err_line(f"Error: relative error ({e:0.6f}) must be less then {err:0.6f}")
        self.add_err_line(f"    expected: {expected:0.6f}")
        self.add_err_line(f"    actual:   {actual:0.6f}")

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
