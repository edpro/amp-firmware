from typing import List, NamedTuple

from tools.common.tests import TestReporter, erel, rel_str
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario

FREQ_REL = 0.01


class TData(NamedTuple):
    f: int


test_data: List[TData] = [
    TData(f=10),
    TData(f=100),
    TData(f=1_000),
    TData(f=10_000),
    TData(f=100_000),
    TData(f=1_000_000),
]


# noinspection PyMethodParameters
class PSTestFreq(Scenario):
    def __init__(self):
        super().__init__("test_freq")

    def on_run(t):
        t.use_edpro_ps()
        t.use_meter()
        t.test_freq()

    def test_freq(t):
        t.edpro_ps.set_mode("ac")
        t.edpro_ps.set_volt(3.0)
        t.meter.set_mode(RigolMode.FREQ_20)
        t.wait(1)

        r = TestReporter(t.tag)

        for d in test_data:
            t.edpro_ps.set_freq(d.f)
            t.wait(0.25)

            real_f = t.meter.measure_freq()
            rel_err = erel(real_f, d.f)

            row = f'f: {d.f}Hz | result: {real_f}'
            row += f' | rel: {rel_str(rel_err)}'

            r.trace(row)
            r.expect_rel(real_f, d.f, FREQ_REL)

        r.print_result()
        t.success &= r.success


if __name__ == "__main__":
    PSTestFreq().run()
