from typing import NamedTuple, List

from tools.common.test import TestReporter, TResult
from tools.scenarious.scenario import Scenario

ABS_ERROR = 0.010
REL_ERROR = 0.02


class TData(NamedTuple):
    volt: float
    range: int


test_data: List[TData] = [
    TData(volt=0.020, range=7),
    TData(volt=0.100, range=7),
    TData(volt=0.500, range=6),
    TData(volt=1.000, range=5),
    TData(volt=2.000, range=4),
    TData(volt=4.000, range=3),
    TData(volt=8.000, range=2),
    TData(volt=16.000, range=1),
    TData(volt=30.000, range=0),
]


# noinspection PyMethodParameters
class MMTestVDC(Scenario):
    def __init__(self):
        super().__init__("test_vdc")

    def on_run(t):
        t.use_edpro_mm()
        t.use_devboard()
        t.use_meter()
        t.use_power()
        t.test_vdc()

    def test_vdc(t):
        t.print_task("test_vdc")
        t.devboard.set_off()

        t.edpro_mm.cmd("mode vdc")
        mm_mode = t.edpro_mm.get_mode()
        t.check_str(mm_mode, "VDC", "Invalid device mode!")

        t.meter.set_vdc_range(0)
        t.power.set_volt(0)
        t.devboard.set_mm_vpow(meas_v=True)
        t.wait(1)

        reporter = TestReporter(t.tag)

        for d in test_data:
            t.meter.set_vdc_range(d.volt)
            t.power.set_volt(d.volt)
            t.wait(1)
            t.meter.measure_vdc()  # duty cycle
            expected = t.meter.measure_vdc()

            t.check_rel(expected, d.volt, 0.1, f"Required voltage does not match")

            values = t.edpro_mm.get_values()
            t.check_str(values.mode, "VDC", "Multimeter mode is invalid")
            t.check(values.finit, "Multimeter result is not finit")

            actual = values.value
            result = TResult(actual, expected, ABS_ERROR, REL_ERROR)
            reporter.trace(result.row_str(f'volt: {d.volt}V'))
            reporter.expect(result)

        t.power.set_volt(0)
        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    MMTestVDC().run()
