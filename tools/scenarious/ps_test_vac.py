from typing import NamedTuple, List

from tools.common.test import TestReporter, TResult
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


class TData(NamedTuple):
    volt: float
    freq: int
    abs: float
    rel: float


VAC_ABS = 0.02
VAC_REL = 0.03

ALL_VOLT = [0, 0.2, 0.4, 1, 2, 3]
ALL_FREQ = [50, 100, 1000, 10_000, 50_000, 100_000]


def make_data(freq: List[int], volt: List[float]) -> List[TData]:
    data = []
    for f in freq:
        for v in volt:
            abs = VAC_ABS if v > 0.2 else 2 * VAC_ABS
            rel = VAC_REL if v > 0.2 else 2 * VAC_REL
            if 100 < f <= 50_000:
                rel += 0
            else:
                rel += 0.01
            data.append(TData(freq=f, volt=v, abs=abs, rel=rel))
    return data


test_data = make_data(freq=ALL_FREQ, volt=ALL_VOLT)


# test_data = make_data(freq=[80_000], volt=ALL_VOLT)


# noinspection PyMethodParameters
class PSTestVAC(Scenario):
    def __init__(self):
        super().__init__("test_vac")

    def on_run(t):
        t.use_devboard()
        t.use_edpro_ps()
        t.use_meter()
        t.test_vac()

    def test_vac(t):
        t.print_task("test_vac")
        t.devboard.set_off()

        t.edpro_ps.set_mode("ac")
        t.edpro_ps.set_volt(0)
        t.edpro_ps.set_freq(1000)
        t.meter.set_mode(RigolMode.VAC_20)
        t.devboard.set_meas_v()
        t.wait(1)

        reporter = TestReporter(t.tag)

        for d in test_data:
            t.edpro_ps.set_volt(d.volt)
            t.edpro_ps.set_freq(d.freq)
            t.wait(0.5)

            t.meter.measure_vac()  # duty cycle
            expected = t.meter.measure_vac()
            expected_diff = 0.05 if d.volt < 0.15 else 0.1
            t.check_abs(expected, d.volt, expected_diff, f"Required voltage does not match")

            actual = t.edpro_ps.get_values().U
            result = TResult(actual, expected, d.abs, d.rel)

            row = result.row_str(f'freq: {d.freq}Hz | volt: {d.volt:0.1f}V')
            reporter.trace(row)
            reporter.expect(result)

        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    PSTestVAC().run()
