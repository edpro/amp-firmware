from enum import Enum

from tools.common.logger import Logger, LoggedError
from tools.edpro_device import EdproPS
from tools.rigol_device import RigolDevice

logger = Logger("ps_cal")


class PSCal(Enum):
    ALL = "ALL"
    VDC = "VDC"
    VAC = "VAC"
    ADC = "ADC"
    AAC = "AAC"


def check(val: bool, message: str):
    if not val:
        logger.throw("Measured value must be about 5V")


def _cal_vdc(ps: EdproPS, rigol: RigolDevice):
    logger.info("calibrate VDC:")
    ps.cmd("mode dc")
    ps.cmd("set l 50")
    v = rigol.measure_dc_20V()
    check(v < v < 6, "Measured value must be about 5V")
    ps.cmd(f"cal vdc {v:0.6f}")
    ps.cmd("set l 0")
    ps.cmd("cal vdcp")


def _cal_adc(ps, rigol):
    logger.info("calibrate ADC:")
    ps.cmd("mode dc")
    ps.cmd("cal adc0")
    # ps.cmd("set l 10")
    # ps.cmd("set l 10")
    logger.error("not implemented")


def _cal_vac(ps, rigol):
    logger.info("calibrate VAC:")
    ps.cmd("mode ac")
    ps.cmd("set f 1000")
    ps.cmd("set l 30")
    v = rigol.measure_ac_20V()
    check(2 < v < 4, "Measured value must be about 3V")
    ps.cmd(f"cal vac {v:0.6f}")
    ps.cmd("set l 0")
    ps.cmd("cal vacp")


def _cal_aac(ps, rigol):
    logger.info("calibrate AAC:")
    logger.error("not implemented")
    pass


def ps_calibration(type: PSCal):
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
        ps.disconnect()
        logger.throw("Invalid device name!")

    # do calibrations

    if type == PSCal.VDC or type == PSCal.ALL:
        _cal_vdc(ps, rigol)

    if type == PSCal.ADC or type == PSCal.ALL:
        _cal_adc(ps, rigol)

    if type == PSCal.VAC or type == PSCal.ALL:
        _cal_vac(ps, rigol)

    if type == PSCal.AAC or type == PSCal.ALL:
        _cal_aac(ps, rigol)

    ps.disconnect()


if __name__ == "__main__":
    try:
        # ps_calibration(PSCal.ALL)
        # ps_calibration(PSCal.VDC)
        # ps_calibration(PSCal.ADC)
        ps_calibration(PSCal.VAC)
        # ps_calibration(PSCal.AAC)
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
