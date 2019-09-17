from typing import List, NamedTuple, Optional

from tools.common.test import TestReporter, abs_str, eabs, erel, rel_str
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


#      +--[V]--+
#      |       |
# (+)--+--R1---+---+
#                  | I = V / R1
# (-)-----R2-------+
#

R1 = 1.0
R2 = 5.6


class TData(NamedTuple):
    c: float  # Current, A
    abs: Optional[float]
    rel: Optional[float]


test_data: List[TData] = [
    TData(c=0.0, abs=0.02, rel=None),
    TData(c=0.1, abs=None, rel=0.04),
    TData(c=0.2, abs=None, rel=0.02),
    TData(c=0.4, abs=None, rel=0.02),
    TData(c=0.6, abs=None, rel=0.02),
]


# noinspection PyMethodParameters
class PSTestADC(Scenario):
    def __init__(self):
        super().__init__("test_adc")

    def on_run(t):
        t.use_edpro_ps()
        t.use_meter()
        t.test_adc()
        t.edpro_ps.set_volt(0)  # turn off due to high current

    def test_adc(t):
        t.edpro_ps.set_mode("dc")
        t.edpro_ps.set_volt(0)
        t.meter.set_mode(RigolMode.VDC_2)
        t.wait(1)

        r = TestReporter(t.tag)

        for d in test_data:
            v = d.c * (R1 + R2)
            t.edpro_ps.set_volt(v)
            t.wait(0.25)

            real_v = t.meter.measure_vdc()
            real_c = real_v / R1
            t.check_abs(real_c, d.c, 0.1, f"Required current does not match")

            result = t.edpro_ps.get_values()
            abs_err = eabs(real_c, result.I) if d.abs else None
            rel_err = erel(real_c, result.I) if d.rel else None

            row = f'c: {d.c}A | expect: {real_c:0.6f} | result: {result.I:0.6f}'
            row += f' | abs: {abs_str(abs_err)}'
            row += f' | rel: {rel_str(rel_err)}'

            r.trace(row)
            r.expect_abs(result.I, real_c, d.abs)
            r.expect_rel(result.I, real_c, d.rel)

        r.print_result()
        t.success &= r.success


if __name__ == "__main__":
    PSTestADC().run()