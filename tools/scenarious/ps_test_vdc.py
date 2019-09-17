from typing import NamedTuple, List, Optional
from tools.common.tests import eabs, erel, TestReporter, abs_str, rel_str
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario

VDC_STEP_ERR = 0.06


class TData(NamedTuple):
    v: float
    abs: Optional[float]
    rel: Optional[float]


test_data: List[TData] = [
    TData(v=0.0, abs=0.05, rel=None),
    TData(v=0.1, abs=0.01, rel=None),
    TData(v=0.2, abs=None, rel=0.04),
    TData(v=0.4, abs=None, rel=0.02),
    TData(v=0.6, abs=None, rel=0.02),
    TData(v=0.8, abs=None, rel=0.02),
    TData(v=1.0, abs=None, rel=0.02),
    TData(v=2.0, abs=None, rel=0.02),
    TData(v=3.0, abs=None, rel=0.02),
    TData(v=4.0, abs=None, rel=0.02),
    TData(v=5.0, abs=None, rel=0.02),
    # test ability to change full range in a proper time
    TData(v=0.0, abs=0.05, rel=None),
    TData(v=5.0, abs=None, rel=0.02),
    TData(v=0.0, abs=0.05, rel=None),
]


# noinspection PyMethodParameters
class PSTestVDC(Scenario):
    def __init__(self):
        super().__init__("test_vdc")

    def on_run(t):
        t.use_edpro_ps()
        t.use_meter()
        t.test_vdc()

    def test_vdc(t):
        t.edpro_ps.set_mode("dc")
        t.edpro_ps.set_volt(0)
        t.meter.set_mode(RigolMode.VDC_20)
        t.wait(1)

        r = TestReporter(t.tag)

        for d in test_data:
            t.edpro_ps.set_volt(d.v)
            t.wait(0.25)

            real_v = t.meter.measure_vdc()
            t.check_abs(real_v, d.v, VDC_STEP_ERR, f"Required voltage does not match")

            result = t.edpro_ps.get_values()
            abs_err = eabs(real_v, result.U) if d.abs else None
            rel_err = erel(real_v, result.U) if d.rel else None

            row = f'v: {d.v}V | expect: {real_v:0.6f} | result: {result.U:0.6f}'
            row += f' | abs: {abs_str(abs_err)}'
            row += f' | rel: {rel_str(rel_err)}'

            r.trace(row)
            r.expect_abs(result.U, real_v, d.abs)
            r.expect_rel(result.U, real_v, d.rel)

        r.print_result()
        t.success &= r.success


if __name__ == "__main__":
    PSTestVDC().run()
