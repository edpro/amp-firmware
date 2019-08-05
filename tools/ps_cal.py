import time

from tools.common.logger import Logger, LoggedError
from tools.edpro_device import EdproPS
from tools.rigol_device import RigolDevice

logger = Logger("ps_cal")


def _cal_vdc(ps: EdproPS, rigol: RigolDevice):
    logger.info("calibrate VDC:")

    r = ps.receive("mode dc")
    if r.get("success") != "1":
        logger.throw("command failed")

    r = ps.receive("set l 50")
    if r.get("success") != "1":
        logger.throw("command failed")

    v = rigol.measure_dc_20V()
    if (v < 4 or v > 6):
        logger.throw("Measured value must be near 5V")

    r = ps.receive(f"cal vdc {v:0.6f}")
    if r.get("success") != "1":
        logger.throw("command failed")

    r = ps.receive("set l 0")
    if r.get("success") != "1":
        logger.throw("command failed")

    r = ps.receive("cal vdcp")
    if r.get("success") != "1":
        logger.throw("command failed")


def _cal_adc(ps, rigol):
    pass


def _cal_vac(ps, rigol):
    pass


def _cal_aac(ps, rigol):
    pass


def ps_calibration():
    # init rigol
    rigol = RigolDevice()
    rigol.connect()

    # init powersource
    ps = EdproPS()
    ps.connect()
    ps.wait_boot_complete()
    ps.send("devmode")

    # check device is really powersourse
    response = ps.receive("i")
    if response.get("name") != "Powersource":
        ps.disconnect()
        logger.throw("Invalid device name!")

    # do calibrations
    _cal_vdc(ps, rigol)
    _cal_adc(ps, rigol)
    _cal_vac(ps, rigol)
    _cal_aac(ps, rigol)

    ps.disconnect()

if __name__ == "__main__":
    try:
        ps_calibration()
        logger.success()
        input("Press <ENTER> to continue...")
    except LoggedError:
        pass
    except Exception:
        raise
