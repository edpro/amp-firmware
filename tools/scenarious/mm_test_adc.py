from typing import NamedTuple, List

from tools.common.test import TestReporter, TResult
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario

ABS_ERROR = 0.05
REL_ERROR = 0.02


class TData(NamedTuple):
    curr: float


test_data: List[TData] = [
    TData(curr=0.020),
    TData(curr=0.050),
    TData(curr=0.100),
    TData(curr=0.500),
]


# noinspection PyMethodParameters
class MMTestADC(Scenario):
    def __init__(self):
        super().__init__("test_adc")

    def on_run(t):
        t.use_edpro_mm()
        t.use_devboard()
        t.use_meter()
        t.use_power()
        t.test_adc()
        t.devboard.set_off()

    def test_adc(t):
        t.print_task("test_adc")
        t.devboard.set_off()

        t.power.set_volt(10)
        t.wait(1)

        t.edpro_mm.cmd("mode adc")
        mm_mode = t.edpro_mm.get_mode()
        t.check_str(mm_mode, "ADC", "Invalid device mode!")

        t.meter.set_mode(RigolMode.ADC_2A)
        t.power.set_current(0.001)
        t.wait(0.5)

        reporter = TestReporter(t.tag)

        for d in test_data:
            t.devboard.set_mm_ipow(meas_i=True)
            t.power.set_current(d.curr)
            t.wait(0.5)

            t.meter.measure_adc()  # duty cycle
            expected = t.meter.measure_adc()
            t.check_rel(expected, d.curr, 0.1, f"Required current does not match")

            values = t.edpro_mm.get_values()
            t.devboard.set_off()

            t.check_str(values.mode, "ADC", "Multimeter mode is invalid")
            t.check(values.finit, "Multimeter result is not finit")

            actual = values.value
            result = TResult(actual, expected, ABS_ERROR, REL_ERROR)
            reporter.trace(result.row_str(f'curr: {d.curr}A'))
            reporter.expect(result)

        t.power.set_volt(0)
        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    MMTestADC().run()
