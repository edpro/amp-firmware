import time
from typing import Tuple, Optional, List

from tools.common.logger import Logger, LoggedError
from tools.edpro_device import EdproPS
from tools.rigol_device import RigolDevice, RigolMode

logger = Logger("ps_test")

VDC_ABS = 0.02
VDC_REL = 0.02
VDC_STEP_ABS = 0.05

VAC_ABS = 0.03
VAC_REL = 0.03
VAC_STEP_ABS = 0.05

FREQ_REL = 0.01


def check(val: bool, message: str):
    if not val:
        logger.throw(message)


def print_table(title: str, records: List[Tuple[bool, str]]):
    logger.info(title)
    for success, msg in records:
        if success:
            logger.trace(msg)
        else:
            logger.error(msg)


def _test_fac(ps: EdproPS, ri: RigolDevice) -> bool:
    logger.info("test F(AC)")
    ri.mode(RigolMode.FREQ_20)
    ps.cmd("mode ac")
    ps.cmd("set l 30")
    time.sleep(1)
    records: List[Tuple[bool, str]] = []
    all_succeed = True
    f = 10
    while f <= 100_000:
        ps.cmd(f"set f {f}")
        time.sleep(0.2)
        ps_val = ps.request_values()
        ri_val = ri.measure_freq()
        e_abs = abs(f - ri_val)
        e_rel = e_abs / abs(ri_val)
        msg = f"expected: {f} | actual: {ri_val:0f} | abs: {e_abs:0f} | rel: {e_rel * 100:0.2f}%"
        success = e_rel <= FREQ_REL

        records.append((success, msg))
        if success:
            logger.success(msg)
        else:
            all_succeed = False
            logger.error(msg)

        if f < 100:
            f += 10
        elif f < 1_000:
            f += 100
        elif f < 10_000:
            f += 1_000
        elif f < 100_000:
            f += 10_000
        else:
            f += 100_000

    print_table("F(AC) test result:", records)

    return all_succeed


def _test_vac(ps: EdproPS, ri: RigolDevice) -> bool:
    logger.info("test VAC")
    ri.mode(RigolMode.VAC_20)
    ps.cmd("mode ac")
    ps.cmd("set l 0")
    ps.cmd("set f 1000")
    time.sleep(1)
    records: List[Tuple[bool, str]] = []
    all_succeed = True

    for level in range(0, 31, 2):
        ps.cmd(f"set l {level}")
        time.sleep(0.2)
        ps_val = ps.request_values()
        ri_val = ri.measure_vac()
        e_abs = abs(ps_val.U - ri_val)
        e_rel = e_abs / abs(ri_val)
        msg = f"expected: {ps_val.U:0.6f} | actual: {ri_val:0.6f} | abs: {e_abs:0.6f} | rel: {e_rel * 100:0.2f}%"
        if level == 0:
            success = e_abs <= VAC_ABS and (0.1 * level - ri_val) < VAC_STEP_ABS
        else:
            success = e_rel <= VAC_REL and (0.1 * level - ri_val) < VAC_STEP_ABS

        records.append((success, msg))
        if success:
            logger.success(msg)
        else:
            all_succeed = False
            logger.error(msg)

    print_table("V(AC) test result (1000Hz):", records)

    return all_succeed


def _test_vdc(ps: EdproPS, ri: RigolDevice) -> bool:
    logger.info("test VDC")
    ri.mode(RigolMode.VDC_20)
    ps.cmd("mode dc")
    ps.cmd("set l 0")
    time.sleep(1)
    records: List[Tuple[bool, str]] = []
    all_succeed = True

    for level in range(0, 51, 2):
        ps.cmd(f"set l {level}")
        ps_val = ps.request_values()
        ri_val = ri.measure_vdc()
        e_abs = abs(ps_val.U - ri_val)
        e_rel = e_abs / abs(ri_val)
        msg = f"expected: {ps_val.U:0.6f} | actual: {ri_val:0.6f} | abs: {e_abs:0.6f} | rel: {e_rel * 100:0.2f}%"
        if level == 0:
            success = e_abs <= VDC_ABS and (0.1 * level - ri_val) < VDC_STEP_ABS
        else:
            success = e_rel <= VDC_REL and (0.1 * level - ri_val) < VDC_STEP_ABS

        records.append((success, msg))
        if success:
            logger.success(msg)
        else:
            all_succeed = False
            logger.error(msg)

    print_table("V(DC) test result:", records)

    return all_succeed


def _init_devices() -> Tuple[EdproPS, RigolDevice]:
    # init rigol
    rigol = RigolDevice()
    rigol.connect()

    # init powersource
    ps = EdproPS()
    ps.connect()
    ps.wait_boot_complete()
    ps.request("devmode")

    # check device is really powersourse
    response = ps.request("i")
    if response.get("name") != "Powersource":
        logger.throw("Invalid device name!")

    return ps, rigol


def _dispose_devices(ps: Optional[EdproPS], ri: Optional[RigolDevice]):
    if ps: ps.close()
    if ri: ri.close()


# def ps_run_test():
#     ps: Optional[EdproPS] = None
#     ri: Optional[RigolDevice] = None


def _run():
    ps: Optional[EdproPS] = None
    ri: Optional[RigolDevice] = None
    try:
        ps, ri = _init_devices()
        # check(_test_vdc(ps, ri), "Test completed with errors")
        # check(_test_vac(ps, ri), "Test completed with errors")
        check(_test_fac(ps, ri), "Test completed with errors")
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        _dispose_devices(ps, ri)


if __name__ == "__main__":
    _run()
