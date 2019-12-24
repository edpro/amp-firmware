from typing import NamedTuple, List, Optional

from tools.common.test import TestReporter, to_amp, TResult
from tools.scenarious.scenario import Scenario


class TData(NamedTuple):
    v: float
    f: int
    abs: Optional[float]
    rel: Optional[float]


ABS_ERROR = 0.01
REL_ERROR = 0.04

ALL_FREQ = [50, 100, 1_000, 10_000, 20_000, 40_000, 80_000]
ALL_VOLT = [0.1, 0.2, 0.4, 0.8, 1.0, 2.0, 4.0, 8.0]


def make_data(freq, volt) -> List[TData]:
    data = []
    for f in freq:
        for v in volt:
            data.append(TData(f=f, v=v, abs=ABS_ERROR, rel=REL_ERROR))
    return data


test_data = make_data(freq=ALL_FREQ, volt=ALL_VOLT)
# test_data = make_data(freq=[1_000], volt=ALL_VOLT)
# test_data = make_data(freq=[80_000], volt=ALL_VOLT)


# noinspection PyMethodParameters
class MMTestVAC(Scenario):
    def __init__(self, fail_fast: bool = False):
        self.fail_fast = fail_fast
        super().__init__("test_vac")

    def on_run(t):
        t.use_devboard()
        t.use_edpro_mm()
        t.use_meter()
        t.use_generator()
        t.test_vac()

        t.generator.set_output_off()
        t.devboard.set_off()

    def test_vac(t):
        t.print_task("test_vac")
        t.devboard.set_off()

        t.edpro_mm.cmd("mode vac")
        mm_mode = t.edpro_mm.get_mode()
        t.check_str(mm_mode, "VAC", "Invalid device mode!")

        t.meter.set_vac_range(0)
        t.generator.set_ac(0.001, 50)
        t.generator.set_output_on()
        t.devboard.set_mm_vgen(meas_v=True)
        t.wait(1)

        reporter = TestReporter(t.tag, t.fail_fast)

        for d in test_data:
            t.meter.set_vac_range(d.v)
            t.generator.set_ac(to_amp(d.v), d.f)
            t.wait(1)

            t.meter.measure_vac()  # duty cycle
            expected = t.meter.measure_vac()
            t.check_rel(expected, d.v, 0.1, f"Required voltage does not match")

            values = t.edpro_mm.get_values()
            t.check_str(values.mode, "VAC", "Multimeter mode is invalid")
            t.check(values.finit, "Multimeter result is not finit")

            actual = values.value
            result = TResult(actual, expected, d.abs, d.rel)

            row = result.row_str(f'freq: {d.f}Hz | volt: {d.v}V')
            reporter.trace(row)
            reporter.expect(result)

        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    # MMTestVAC().run()
    MMTestVAC(fail_fast=True).run()
