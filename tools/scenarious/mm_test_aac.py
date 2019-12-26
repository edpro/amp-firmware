from typing import NamedTuple, List, Optional

from tools.common.test import TestReporter, TResult
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


class TData(NamedTuple):
    c: float
    f: int
    abs: Optional[float]
    rel: Optional[float]


ABS_ERROR = 0.01
REL_ERROR = 0.04

ALL_FREQ = [50, 100, 1_000, 10_000, 20_000]
ALL_CURR = [0.040, 0.080, 0.160]


def make_data(freq, curr) -> List[TData]:
    data = []
    for f in freq:
        for c in curr:
            data.append(TData(f=f, c=c, abs=ABS_ERROR, rel=REL_ERROR))
    return data


slow_data = make_data(
    freq=[50, 100, 1_000, 10_000, 20_000],
    curr=[0.040, 0.080, 0.160])

fast_data = make_data(
    freq=[100, 10_000, 20_000],
    curr=[0.040, 0.080, 0.160])

custom_data = None


# noinspection PyMethodParameters
class MMTestAAC(Scenario):
    def __init__(self, fail_fast: bool = False, run_fast: bool = False):
        self.fail_fast = fail_fast

        if run_fast:
            self.data = fast_data
        elif custom_data is not None:
            self.data = custom_data
        else:
            self.data = slow_data

        super().__init__("test_vac")

    def on_run(t):
        t.use_devboard()
        t.use_edpro_mm()
        t.use_meter()
        t.use_generator()
        t.test_aac()

        t.generator.set_output_off()
        t.devboard.set_off()

    def test_aac(t):
        t.print_task("test_aac")
        t.devboard.set_off()

        t.edpro_mm.cmd("mode aac")
        mm_mode = t.edpro_mm.get_mode()
        t.check_str(mm_mode, "AAC", "Invalid device mode!")

        t.meter.set_mode(RigolMode.AAC_2A)
        t.generator.set_ac(0.001, 50)
        t.generator.set_output_on()
        t.devboard.set_mm_igen(meas_i=True)
        t.wait(1)

        reporter = TestReporter(t.tag, t.fail_fast)

        owon_max_amplitude = 25
        circuit_max_current = 0.165
        effective_r = owon_max_amplitude / circuit_max_current

        for d in t.data:
            t.generator.set_ac(d.c * effective_r, d.f)
            t.wait(1)

            t.meter.measure_aac()  # duty cycle
            expected = t.meter.measure_aac()
            t.check_rel(expected, d.c, 0.1, f"Required current does not match")

            values = t.edpro_mm.get_values()
            t.check_str(values.mode, "AAC", "Multimeter mode is invalid")
            t.check(values.finit, "Multimeter result is not finit")

            actual = values.value
            result = TResult(actual, expected, d.abs, d.rel)

            row = result.row_str(f'freq: {d.f}Hz | curr: {d.c}A')
            reporter.trace(row)
            reporter.expect(result)

        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    MMTestAAC().run()
    # MMTestVAC(fail_fast=True).run()
