from typing import List, NamedTuple

from tools.common.test import TestReporter, TResult
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario

ADC_ABS = 0.02
ADC_REL = 0.04
LOAD_R = 10


class TData(NamedTuple):
    curr: float
    abs: float
    rel: float


test_data: List[TData] = [
    TData(curr=0.0, abs=ADC_ABS, rel=ADC_REL),
    TData(curr=0.1, abs=ADC_ABS, rel=ADC_REL),
    TData(curr=0.2, abs=ADC_ABS, rel=ADC_REL),
    TData(curr=0.4, abs=ADC_ABS, rel=ADC_REL),
]


# noinspection PyMethodParameters
class PSTestADC(Scenario):
    def __init__(self):
        super().__init__("test_adc")

    def on_run(t):
        t.use_devboard()
        t.use_edpro_ps()
        t.use_meter()
        t.test_adc()
        # turn off due to high current
        t.edpro_ps.set_volt(0)

    def test_adc(t):
        t.devboard.set_off()
        t.edpro_ps.set_mode("dc")
        t.edpro_ps.set_volt(0)
        t.meter.set_mode(RigolMode.ADC_2A)
        t.devboard.set_pp_load(1, meas_i=True)
        t.wait(1)

        reporter = TestReporter(t.tag)

        for d in test_data:
            ps_voltage = d.curr * LOAD_R
            t.edpro_ps.set_volt(ps_voltage)
            t.wait(0.5)

            expected = -t.meter.measure_adc()
            t.check_abs(expected, d.curr, 0.1, f"Required current does not match")

            actual = t.edpro_ps.get_values().I
            result = TResult(actual, expected, d.abs, d.rel)

            row = result.row_str(f'curr: {d.curr}A')
            reporter.trace(row)
            reporter.expect(result)

        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    PSTestADC().run()
