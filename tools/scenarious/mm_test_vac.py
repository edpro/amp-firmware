from typing import NamedTuple, List, Optional
from tools.common.test import eabs, erel, TestReporter, abs_str, rel_str, to_amp
from tools.scenarious.scenario import Scenario


class TData(NamedTuple):
    v: float
    f: int
    abs: Optional[float]
    rel: Optional[float]


ALL_FREQ = [50, 100, 1_000, 10_000, 20_000, 40_000, 80_000]
ALL_VOLT = [0.1, 0.2, 0.4, 0.8, 1.0, 2.0, 4.0, 8.0]


def make_data(freq, volt) -> List[TData]:
    data = []
    for f in freq:
        for v in volt:
            abs_err = 0.01 if v <= 0.1 else None
            rel_err = 0.04 if v > 0.1 else None
            data.append(TData(f=f, v=v, abs=abs_err, rel=rel_err))
    return data


# test_data = make_data(freq=ALL_FREQ, volt=ALL_VOLT)
test_data = make_data(freq=[80_000], volt=ALL_VOLT)


# noinspection PyMethodParameters
class MMTestVAC(Scenario):
    def __init__(self):
        super().__init__("test_vac")

    def on_run(t):
        t.use_edpro_mm()
        t.use_meter()
        t.use_generator()
        t.test_vac()

    def test_vac(t):
        t.print_task("test_vac")
        t.edpro_mm.cmd("mode ac")
        mm_mode = t.edpro_mm.get_mode()
        t.check_str(mm_mode, "VAC", "Invalid device mode!")

        t.meter.set_vac_range(0)
        t.generator.set_ac(0.001, 50)
        t.wait(1)

        r = TestReporter(t.tag)

        for d in test_data:
            t.meter.set_vac_range(d.v)
            t.generator.set_ac(to_amp(d.v), d.f)
            t.wait(1)

            t.meter.measure_vac()  # duty cycle
            real_v = t.meter.measure_vac()
            t.check_rel(real_v, d.v, 0.1, f"Required voltage does not match")

            result = t.edpro_mm.get_values()
            t.check_str(result.mode, "VAC", "Multimeter mode is invalid")
            t.check(result.finit, "Multimeter result is not finit")

            abs_err = eabs(real_v, result.value) if d.abs else None
            rel_err = erel(real_v, result.value) if d.rel else None

            row = f'f: {d.f}Hz | v: {d.v}V | expect: {real_v:0.6f} | result: {result.value:0.6f}'
            row += f' | abs: {abs_str(abs_err)}'
            row += f' | rel: {rel_str(rel_err)}'

            r.trace(row)
            r.expect_abs(result.value, real_v, d.abs)
            r.expect_rel(result.value, real_v, d.rel)

        r.print_result()
        t.success &= r.success


if __name__ == "__main__":
    MMTestVAC().run()
