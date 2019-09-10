import time

from math import sqrt

from tools.common.logger import Logger, LoggedError
from tools.common.tests import erel, TestReporter, eabs
from tools.devices.rigol_meter import RigolMode
from tools.mm_context import MMContext

logger = Logger("mm_test")


def to_amp(v: float) -> float:
    return v * 2.0 * sqrt(2)


def from_amp(amp: float) -> float:
    return amp / 2.0 / sqrt(2)


def check(val: bool, message: str):
    if not val:
        logger.throw(message)


def _test_vac(c: MMContext):
    c.mm.cmd("mode ac")
    t = TestReporter("test_vac")
    check(c.mm.request_mode() == "VAC", "Require multimeter is in VAC mode")

    rigol_mode = RigolMode.VAC_2
    c.meter.mode(rigol_mode)
    c.gen.set_ac(0.001, 50)
    time.sleep(1)

    for freq in [50, 100, 1_000, 10_000, 20_000, 40_000, 80_000]:
        for v in [0, 0.1, 0.2, 0.4, 0.8, 1.0, 2.0, 4.0, 8.0]:

            if v <= 1:
                if rigol_mode != RigolMode.VAC_2:
                    rigol_mode = RigolMode.VAC_2
                    c.meter.mode(rigol_mode)
            else:
                if rigol_mode != RigolMode.VAC_20:
                    rigol_mode = RigolMode.VAC_20
                    c.meter.mode(rigol_mode)

            if v == 0:
                c.gen.set_ac(0.001, freq)
            else:
                c.gen.set_ac(to_amp(v), freq)

            time.sleep(1.0)

            c.meter.measure_vac()  # duty cycle
            expected = c.meter.measure_vac()
            actual = c.mm.request_value()
            ea = eabs(expected, actual)
            er = erel(expected, actual)
            t.trace(
                f"f: {freq}Hz | v: {v}V | expected: {expected:0.6f} | actual: {actual:0.6f} | abs: {ea:0.6f} | rel: {er * 100:0.2f}%")
            t.expect_abs_rel(expected, actual, 0.02, 0.04)

    t.print_result()
    return t.success


def _test_vdc(c: MMContext):
    c.mm.cmd("mode dc")
    t = TestReporter("test_vdc")
    check(c.mm.request_mode() == "VDC", "Require multimeter is in VDC mode")

    rigol_mode = RigolMode.VDC_200m
    c.meter.mode(rigol_mode)
    time.sleep(1)

    for v in [0.001, 0.010, 0.100, 1.0, 1.1, 10.0, 20.0, 30.0]:

        if v <= 0.1:
            if rigol_mode != RigolMode.VDC_200m:
                rigol_mode = RigolMode.VDC_200m
                c.meter.mode(rigol_mode)
        elif v <= 1.0:
            if rigol_mode != RigolMode.VDC_2:
                rigol_mode = RigolMode.VDC_2
                c.meter.mode(rigol_mode)
        elif v <= 10.0:
            if rigol_mode != RigolMode.VDC_20:
                rigol_mode = RigolMode.VDC_20
                c.meter.mode(rigol_mode)
        else:
            rigol_mode = RigolMode.VDC_200
            c.meter.mode(rigol_mode)

        c.power.set_volt(v)
        time.sleep(1)

        c.meter.measure_vdc() # duty cycle
        expected = c.meter.measure_vdc()
        actual = c.mm.request_value()
        ea = eabs(expected, actual)
        er = erel(expected, actual)
        t.trace(
            f"v: {v}V | expected: {expected:0.6f} | actual: {actual:0.6f} | abs: {ea:0.6f} | rel: {er * 100:0.2f}%")
        t.expect_abs_rel(expected, actual, 0.01, 0.04)

    t.print_result()
    return t.success


def mm_run_test_vac():
    c = MMContext()
    try:
        c.init()
        _test_vac(c)
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        c.dispose()


def mm_run_test_vdc():
    c = MMContext()
    try:
        c.init()
        _test_vdc(c)
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        c.dispose()


def main():
    c = MMContext()
    try:
        c.init()
        # check(_test_vac(c), "VAC test failed!")
        check(_test_vdc(c), "VDC test failed!")
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        c.dispose()


if __name__ == "__main__":
    main()
