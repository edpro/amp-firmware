from typing import NamedTuple, List

from tools.common.test import TestReporter, TResult
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario

VDC_STEP_ABS = 0.06
VDC_ABS = 0.04
VDC_REL = 0.02


class TData(NamedTuple):
    volt: float
    abs: float
    rel: float


test_data: List[TData] = [
    TData(volt=0.0, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=0.1, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=0.2, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=0.4, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=0.6, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=0.8, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=1.0, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=2.0, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=3.0, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=4.0, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=5.0, abs=VDC_ABS, rel=VDC_REL),
    # test ability to change full range in a proper time
    TData(volt=0.0, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=5.0, abs=VDC_ABS, rel=VDC_REL),
    TData(volt=0.0, abs=VDC_ABS, rel=VDC_REL),
]


# noinspection PyMethodParameters
class PSTestVDC(Scenario):
    def __init__(self):
        super().__init__("test_vdc")

    def on_run(t):
        t.use_devboard()
        t.use_edpro_ps()
        t.use_meter()
        t.test_vdc()

    def test_vdc(t):
        t.devboard.set_off()
        t.edpro_ps.set_mode("dc")
        t.edpro_ps.set_volt(0)
        t.meter.set_mode(RigolMode.VDC_20)
        t.devboard.set_meas_v()
        t.wait(1)

        reporter = TestReporter(t.tag)

        for d in test_data:
            t.edpro_ps.set_volt(d.volt)
            t.wait(0.5)

            expected = t.meter.measure_vdc()
            t.check_abs(expected, d.volt, VDC_STEP_ABS, f"Required voltage does not match")

            actual = t.edpro_ps.get_values().U
            result = TResult(actual, expected, d.abs, d.rel)
            reporter.trace(result.row_str(f'volt: {d.volt}V'))
            reporter.expect(result)

        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    PSTestVDC().run()
