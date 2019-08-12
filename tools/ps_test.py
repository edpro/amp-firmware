from typing import Tuple, Optional, List

from tools.common.logger import Logger, LoggedError
from tools.edpro_device import EdproPS
from tools.rigol_device import RigolDevice, RigolMode

logger = Logger("ps_test")

VDC_MAX_ABS = 0.02
VDC_MAX_REL = 0.02
VDC_MAX_LEVEL = 0.05


def check(val: bool, message: str):
    if not val:
        logger.throw(message)


def _test_vdc(ps: EdproPS, ri: RigolDevice) -> bool:
    logger.info("test VDC")
    ri.mode(RigolMode.VDC_20)
    ps.cmd("mode dc")
    ps.cmd("set l 0")
    records: List[Tuple[bool, str]] = []

    for l in range(0, 50, 2):
        ps.cmd(f"set l {l}")
        ps_val = ps.request_values()
        ri_val = ri.measure_vdc()
        e_abs = abs(ps_val.U - ri_val)
        e_rel = e_abs / abs(ri_val)
        msg = f"expected: {ps_val.U:0.6f} | actual: {ri_val:0.6f} | abs: {e_abs:0.6f} | rel: {e_rel * 100:0.2f}%"
        if l == 0:
            success = e_abs <= VDC_MAX_ABS and (0.1 * l - ri_val) < VDC_MAX_LEVEL
        else:
            success = e_rel <= VDC_MAX_REL and (0.1 * l - ri_val) < VDC_MAX_LEVEL

        records.append((success, msg))
        if success:
            logger.success(msg)
        else:
            logger.error(msg)

    logger.trace("Result:")
    all_succeed = True
    for success, msg in records:
        if success:
            logger.trace(msg)
        else:
            all_succeed = True
            logger.error(msg)

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


def ps_run_test():
    ps: Optional[EdproPS] = None
    ri: Optional[RigolDevice] = None


def _run():
    ps: Optional[EdproPS] = None
    ri: Optional[RigolDevice] = None
    try:
        ps, ri = _init_devices()
        _test_vdc(ps, ri)
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        _dispose_devices(ps, ri)


if __name__ == "__main__":
    _run()
