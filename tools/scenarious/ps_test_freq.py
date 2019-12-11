from typing import List, NamedTuple

from tools.common.test import TestReporter, TResult
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario

FREQ_REL = 0.01
FREQ_ABS = 1


class TData(NamedTuple):
    freq: int


test_data: List[TData] = [
    TData(freq=10),
    TData(freq=100),
    TData(freq=1_000),
    TData(freq=10_000),
    TData(freq=100_000),
    TData(freq=1_000_000),
]


# noinspection PyMethodParameters
class PSTestFreq(Scenario):
    def __init__(self):
        super().__init__("test_freq")

    def on_run(t):
        t.use_devboard()
        t.use_edpro_ps()
        t.use_meter()
        t.test_freq()

    def test_freq(t):
        t.devboard.set_off()
        t.edpro_ps.set_mode("ac")
        t.edpro_ps.set_volt(3.0)
        t.meter.set_mode(RigolMode.FREQ_20)
        t.devboard.set_meas_v()
        t.wait(1)

        reporter = TestReporter(t.tag)

        for d in test_data:
            t.edpro_ps.set_freq(d.freq)
            t.wait(0.5)

            expected = d.freq
            actual = t.meter.measure_freq()
            result = TResult(actual, expected, FREQ_ABS, FREQ_REL)

            row = f'freq: {d.freq:8}Hz' \
                  f' | actual: {result.actual:8.0f}' \
                  f' | abs: {result.abs_err:4.0f}' \
                  f' | rel: {result.rel_str()}'
            reporter.trace(row)
            reporter.expect(result)

        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    PSTestFreq().run()
