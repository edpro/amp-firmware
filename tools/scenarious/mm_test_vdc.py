from typing import NamedTuple, List, Optional

from tools.common.tests import eabs, erel, TestReporter, abs_str, rel_str
from tools.scenarious.scenario import Scenario


class TRecord(NamedTuple):
    v: float
    range: int
    abs: Optional[float]
    rel: Optional[float]


test_records: List[TRecord] = [
    TRecord(v=0.020, range=7, abs=0.010, rel=None),
    TRecord(v=0.100, range=7, abs=0.010, rel=0.05),
    TRecord(v=0.500, range=6, abs=None, rel=0.02),
    TRecord(v=1.000, range=5, abs=None, rel=0.02),
    TRecord(v=2.000, range=4, abs=None, rel=0.02),
    TRecord(v=4.000, range=3, abs=None, rel=0.02),
    TRecord(v=8.000, range=2, abs=None, rel=0.02),
    TRecord(v=16.000, range=1, abs=None, rel=0.02),
    TRecord(v=30.000, range=0, abs=None, rel=0.02),
]


# noinspection PyMethodParameters
class MMTestVDC(Scenario):
    def __init__(self):
        super().__init__("test_vdc")

    def on_run(t):
        t.use_edpro_mm()
        t.use_meter()
        t.use_power()
        t.test_vdc()

    def test_vdc(t):
        t.edpro_mm.cmd("mode dc")
        mm_mode = t.edpro_mm.get_mode()
        t.check_str(mm_mode, "VDC", "Invalid device mode!")

        t.meter.set_vdc_range(0)
        t.power.set_vdc(0)
        t.wait(1)

        r = TestReporter(t.tag)

        for rec in test_records:
            t.meter.set_vdc_range(rec.v)
            t.power.set_vdc(rec.v)
            t.wait(1)
            t.meter.measure_vdc()  # duty cycle
            real_v = t.meter.measure_vdc()
            t.check_rel(real_v, rec.v, 0.1, f"Required voltage does not match")

            result = t.edpro_mm.get_result()
            t.check_str(result.mode, "VDC", "Multimeter mode is invalid")
            t.check(result.finit, "Multimeter result is not finit")

            abs_err = None
            if (rec.abs is not None):
                abs_err = eabs(real_v, result.value)

            rel_err = None
            if (rec.rel is not None):
                rel_err = erel(real_v, result.value)

            row = f'v: {rec.v}V | expect: {real_v:0.6f} | result: {result.value:0.6f}'
            row += f' | abs: {abs_str(abs_err)}'
            row += f' | rel: {rel_str(rel_err)}'

            r.trace(row)
            r.expect_int(result.gain, rec.range, "Measurement range is not valid")
            r.expect_abs(result.value, real_v, rec.abs)
            r.expect_rel(result.value, real_v, rec.rel)

        t.power.set_vdc(0)
        r.print_result()
        t.success &= r.success


if __name__ == "__main__":
    MMTestVDC().run()
