from typing import NamedTuple, List, Optional
from tools.common.tests import eabs, erel, TestReporter, abs_str, rel_str
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


class TData(NamedTuple):
    v: float
    f: int
    abs: Optional[float]
    rel: Optional[float]


ALL_VOLT = [0, 0.2, 0.4, 0.6, 1, 2, 3]
ALL_FREQ = [50, 100, 1000, 10_000, 50_000, 100_000]


def make_data(freq: List[int], volt: List[float]) -> List[TData]:
    data = []
    for f in freq:
        for v in volt:
            if f < 100:
                abs_err = 0.03 if v < 0.1 else None
                rel_err = 0.04 if v > 0.1 else None
            else:
                abs_err = 0.03 if v < 0.1 else None
                rel_err = 0.03 if v > 0.1 else None
            data.append(TData(f=f, v=v, abs=abs_err, rel=rel_err))
    return data


test_data = make_data(freq=ALL_FREQ, volt=ALL_VOLT)
# test_data = make_data(freq=[80_000], volt=ALL_VOLT)


# noinspection PyMethodParameters
class MMTestVAC(Scenario):
    def __init__(self):
        super().__init__("test_vac")

    def on_run(t):
        t.use_edpro_ps()
        t.use_meter()
        t.test_vac()

    def test_vac(t):
        t.edpro_ps.set_mode("ac")
        t.edpro_ps.set_volt(0)
        t.edpro_ps.set_freq(1000)
        t.meter.set_mode(RigolMode.VAC_20)
        t.wait(1)

        r = TestReporter(t.tag)

        for d in test_data:
            t.edpro_ps.set_volt(d.v)
            t.edpro_ps.set_freq(d.f)
            t.wait(0.5)

            t.meter.measure_vac()  # duty cycle
            real_v = t.meter.measure_vac()
            t.check_abs(real_v, d.v, 0.1, f"Required voltage does not match")

            result = t.edpro_ps.get_values()
            abs_err = eabs(real_v, result.U) if d.abs else None
            rel_err = erel(real_v, result.U) if d.rel else None

            row = f'f: {d.f}Hz | v: {d.v}V | expect: {real_v:0.6f} | result: {result.U:0.6f}'
            row += f' | abs: {abs_str(abs_err)}'
            row += f' | rel: {rel_str(rel_err)}'

            r.trace(row)
            r.expect_abs(result.U, real_v, d.abs)
            r.expect_rel(result.U, real_v, d.rel)

        r.print_result()
        t.success &= r.success


if __name__ == "__main__":
    MMTestVAC().run()
