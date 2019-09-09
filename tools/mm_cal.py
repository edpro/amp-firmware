import time

from math import sqrt

from tools.common.logger import Logger, LoggedError
from tools.common.screen import prompt
from tools.common.tests import erel
from tools.devices.rigol_meter import RigolMode
from tools.mm_context import MMContext

logger = Logger("mm_cal")


def to_amp(v: float) -> float:
    return v * 2.0 * sqrt(2)


def from_amp(amp: float) -> float:
    return amp / 2.0 / sqrt(2)


def check(val: bool, message: str):
    if not val:
        logger.throw(message)


def _cal_ac0(c: MMContext):
    c.mm.cmd("mode ac")
    c.mm.cmd("cal ac0")


def _cal_vac_values(c: MMContext):
    freq = 1000
    c.mm.cmd("mode ac")
    c.meter.mode(RigolMode.VAC_20)

    # point 1
    expected_v = 0.1
    c.gen.set_ac(to_amp(expected_v), freq)
    time.sleep(0.5)
    actual_v = c.meter.measure_vac()
    check(erel(expected_v, actual_v) < 0.1, "Expected AC input ~ 0.1V")
    c.mm.cmd(f"cal vac 1 {actual_v:0.6f}")

    # point 2
    expected_v = 1.0
    c.gen.set_ac(to_amp(expected_v), freq)
    time.sleep(0.5)
    actual_v = c.meter.measure_vac()
    check(erel(expected_v, actual_v) < 0.1, "Expected AC input ~ 1.0V")
    c.mm.cmd(f"cal vac 2 {actual_v:0.6f}")

    # point 3
    expected_v = from_amp(25)  # maximum GENERATOR amplitude
    c.gen.set_ac(to_amp(expected_v), freq)
    time.sleep(0.5)
    actual_v = c.meter.measure_vac()
    check(erel(expected_v, actual_v) < 0.1, "Expected AC input ~ 10V")
    c.mm.cmd(f"cal vac 3 {actual_v:0.6f}")


def mm_run_calibration():
    ctx = MMContext()
    try:
        ctx.init()
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        ctx.dispose()


def mm_run_cal_vac():
    c = MMContext()
    try:
        c.init()
        _cal_vac(c)
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        c.dispose()


def mm_run_cal_vdc():
    c = MMContext()
    try:
        c.init()
        # _cal_vac(c)
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        c.dispose()


def _cal_vac(c: MMContext):
    is_done: bool = False

    choise = prompt("Short V<->CON wires on multimeter. <Enter> - continue, <s> - skip: ")
    if choise == "":
        is_done = False
        while True:
            try:
                _cal_ac0(c)
                is_done = True
                break
            except LoggedError:
                choise = prompt("<Enter> - continue, <r> - retry: ")
                if choise == "":
                    break
            except Exception:
                raise

    choise = prompt("Connect GENERATOR & RIGOL. <Enter> - continue, <s> - skip: ")
    if choise == "":
        is_done = False
        while True:
            try:
                _cal_vac_values(c)
                is_done = True
                break
            except LoggedError:
                choise = prompt("<Enter> - continue, <r> - retry: ")
                if choise == "":
                    break
            except Exception:
                raise

    if is_done:
        c.mm.cmd("conf s")
        logger.success()


def main():
    ctx = MMContext()
    try:
        ctx.init()
        # _cal_ac0(ctx)
        _cal_vac_values(ctx)
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        ctx.dispose()


if __name__ == "__main__":
    main()
