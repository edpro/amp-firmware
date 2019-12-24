from itertools import chain
from typing import NamedTuple, List

from tools.common.test import TestReporter, TResult
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario

LOAD_R = 10


class TData(NamedTuple):
    freq: int
    curr: float
    abs: float
    rel: float


def make_data(freq: int, e_abs: float, e_rel: float) -> List[TData]:
    return [
        TData(freq, curr=0.00, abs=e_abs, rel=e_rel),
        TData(freq, curr=0.05, abs=e_abs, rel=e_rel),
        TData(freq, curr=0.10, abs=e_abs, rel=e_rel),
        TData(freq, curr=0.20, abs=e_abs, rel=e_rel),
    ]


test_data = list(chain(
    make_data(freq=50, e_abs=0.04, e_rel=0.04),
    make_data(freq=100, e_abs=0.04, e_rel=0.04),
    make_data(freq=1000, e_abs=0.04, e_rel=0.04),
    make_data(freq=10_000, e_abs=0.04, e_rel=0.04),
    make_data(freq=10_000, e_abs=0.04, e_rel=0.04),
    make_data(freq=20_000, e_abs=0.05, e_rel=0.50),
))


# noinspection PyMethodParameters
class PSTestAAC(Scenario):
    def __init__(self):
        super().__init__("test_aac")

    def on_run(t):
        t.use_devboard()
        t.use_edpro_ps()
        t.use_meter()
        t.test_vac()

    def test_vac(t):
        t.print_task("test_adc")
        t.devboard.set_off()

        t.edpro_ps.set_mode("ac")
        t.edpro_ps.set_volt(0)
        t.meter.set_mode(RigolMode.AAC_2A)
        t.devboard.set_pp_load(1, meas_i=True)
        t.wait(1)

        reporter = TestReporter(t.tag)

        for d in test_data:
            voltage = d.curr * LOAD_R
            t.edpro_ps.set_volt(voltage)
            t.edpro_ps.set_freq(d.freq)
            t.wait(0.5)

            t.meter.measure_aac()  # duty cycle
            expected = t.meter.measure_aac()
            expected_diff = 0.02 if d.curr < 0.1 else 0.05
            t.check_abs(expected, d.curr, expected_diff, f"Required current does not match")

            actual = t.edpro_ps.get_values().I
            result = TResult(actual, expected, d.abs, d.rel)

            row = result.row_str(f'freq: {d.freq}Hz | curr: {d.curr:0.2f}A')
            reporter.trace(row)
            reporter.expect(result)

        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    PSTestAAC().run()
