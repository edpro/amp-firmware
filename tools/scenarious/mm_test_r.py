from typing import NamedTuple, List

from tools.common.test import TestReporter, TResult
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario

ABS_ERROR = 1.0
REL_ERROR = 0.02


class TData(NamedTuple):
    volt: float


test_data: List[TData] = [
    TData(volt=0.020),
    TData(volt=0.500),
    TData(volt=1),
    TData(volt=2),
    TData(volt=4),
    TData(volt=8),
    TData(volt=16),
    TData(volt=-10),
    TData(volt=-2),
    TData(volt=-0.2),
]


# noinspection PyMethodParameters
class MMTestR(Scenario):
    def __init__(self):
        super().__init__("test_r")

    def on_run(t):
        t.use_edpro_mm()
        t.use_devboard()
        t.use_meter()
        t.test_r()

        t.devboard.set_off()

    def test_r(t):
        t.print_task("test R:")
        t.devboard.set_off()
        t.edpro_mm.cmd("mode r")

        # test OL
        t.logger.info("test OL")
        t.wait(0.5)
        v = t.edpro_mm.get_values()
        t.check(v.mode == "R", "Invalid meter mode: must be 'R'")
        t.check(not v.finit, "Invalid result: must be 'OL'")

        reporter = TestReporter(t.tag)

        # cal 0
        t.logger.info("test 0")
        t.devboard.set_mm_rgnd()
        t.wait(0.5)
        v = t.edpro_mm.get_values()
        t.check(v.mode == "R", "Invalid meter mode: must be 'R'")
        t.check(v.finit, "Invalid result: must finit")

        result = TResult(v.value, 0, ABS_ERROR, REL_ERROR)
        reporter.trace(result.row_str(f"R: {0}"))
        reporter.expect(result)

        def test_r(n1: int, n2: int, r: int, rigol_mode: RigolMode):
            t.logger.info(f"tesr R: {r}")
            t.devboard.set_meas_r(n1, n2)
            t.meter.set_mode(rigol_mode)
            t.wait(1)
            expected = t.meter.measure_r()
            t.check_rel(expected, r, 0.1, "Cannot set required resistance")
            t.devboard.set_mm_rsel(n1, n2)
            t.wait(1)

            # noinspection PyShadowingNames
            v = t.edpro_mm.get_values()
            t.check(v.mode == "R", "Invalid meter mode: must be 'R'")
            t.check(v.finit, "Invalid result: must finit")

            # noinspection PyShadowingNames
            result = TResult(v.value, expected, ABS_ERROR, REL_ERROR)
            reporter.trace(result.row_str(f"R: {r}"))
            reporter.expect(result)

            t.check_rel(v.value, r, 1, "Invalid measurement")

        test_r(1, 6, r=5, rigol_mode=RigolMode.R_2K)
        test_r(2, 7, r=1_000, rigol_mode=RigolMode.R_20K)
        test_r(3, 8, r=10_000, rigol_mode=RigolMode.R_200K)
        test_r(4, 9, r=100_000, rigol_mode=RigolMode.R_2M)
        test_r(5, 10, r=900_000, rigol_mode=RigolMode.R_10M)

        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    MMTestR().run()
