from itertools import chain
from typing import NamedTuple, List, Optional
from tools.common.test import eabs, erel, TestReporter, abs_str, rel_str
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
    f: int
    c: float
    abs: Optional[float]
    rel: Optional[float]


def make_data(f: int, abs: float, rel: float) -> List[TData]:
    return [
        TData(f=f, c=0.00, abs=abs, rel=None),
        TData(f=f, c=0.05, abs=abs, rel=None),
        TData(f=f, c=0.10, abs=abs, rel=None),
        TData(f=f, c=0.15, abs=None, rel=rel),
        TData(f=f, c=0.20, abs=None, rel=rel),
    ]


test_data = list(chain(
    make_data(f=50, abs=0.03, rel=0.2),
    make_data(f=100, abs=0.03, rel=0.2),
    make_data(f=1_000, abs=0.02, rel=0.05),
    make_data(f=10_000, abs=0.02, rel=0.05),
    make_data(f=100_000, abs=0.02, rel=0.05),
))


# noinspection PyMethodParameters
class PSTestAAC(Scenario):
    def __init__(self):
        super().__init__("test_aac")

    def on_run(t):
        t.use_edpro_ps()
        t.use_meter()
        t.test_vac()

    def test_vac(t):
        t.edpro_ps.set_mode("ac")
        t.edpro_ps.set_volt(0)
        t.meter.set_mode(RigolMode.VAC_2)
        t.wait(1)

        r = TestReporter(t.tag)

        for d in test_data:
            v = d.c * (R1 + R2)
            t.edpro_ps.set_volt(v)
            t.edpro_ps.set_freq(d.f)
            t.wait(1.0)

            t.meter.measure_vac()  # duty cycle
            real_v = t.meter.measure_vac()
            real_c = real_v / R1
            t.check_abs(real_c, d.c, 0.05, f"Required current does not match")

            result = t.edpro_ps.get_values()
            abs_err = eabs(real_c, result.I) if d.abs else None
            rel_err = erel(real_c, result.I) if d.rel else None

            row = f'f: {d.f}Hz | c: {d.c}A | expect: {real_c:0.6f} | result: {result.I:0.6f}'
            row += f' | abs: {abs_str(abs_err)}'
            row += f' | rel: {rel_str(rel_err)}'

            r.trace(row)
            r.expect_abs(result.I, real_c, d.abs)
            r.expect_rel(result.I, real_c, d.rel)

        r.print_result()
        t.success &= r.success


if __name__ == "__main__":
    PSTestAAC().run()
