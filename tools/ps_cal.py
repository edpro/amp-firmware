import time
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
        logger.throw(message)


def _cal_vdc(ps: EdproPS, rigol: RigolDevice):
    logger.info("calibrate VDC:")
    ps.cmd("mode dc")
    ps.cmd("set l 50")
    time.sleep(0.25)
    v = rigol.measure_dc_20V()
    check(4 < v < 6, "Measured value must be about 5V")
    ps.cmd(f"cal vdc {v:0.6f}")
    ps.cmd("set l 0")
    ps.cmd("cal vdcp")


def _cal_adc(ps, rigol):
    logger.info("calibrate ADC:")
    ps.cmd("mode dc")
    ps.cmd("set l 0")
    time.sleep(0.25)
    ps.cmd("cal adc0")
    ps.cmd("set l 10")
    time.sleep(0.25)
    v = rigol.measure_dc_2V()
    check(0.1 < v < 0.2, "Measured value must be about 0.15A")
    ps.cmd(f"cal adc {v:0.6f}")


def _cal_vac(ps, rigol):
    logger.info("calibrate VAC:")
    ps.cmd("mode ac")
    ps.cmd("set f 1000")
    ps.cmd("set l 30")
    time.sleep(0.25)
    v = rigol.measure_ac_20V()
    check(2 < v < 4, "Measured value must be about 3V")
    ps.cmd(f"cal vac {v:0.6f}")
    ps.cmd("set l 0")
    ps.cmd("cal vacp")


def _cal_aac(ps, rigol):
    logger.info("calibrate AAC:")
    ps.cmd("mode ac")
    ps.cmd("set l 0")
    ps.cmd("set f 1000")
    time.sleep(0.25)
    ps.cmd("cal aac0")
    ps.cmd("set l 10")
    time.sleep(0.25)
    v = rigol.measure_ac_2V()
    check(0.1 < v < 0.2, "Measured value must be about 0.15A")
    ps.cmd(f"cal aac {v:0.6f}")
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

    ps.cmd("conf s")
    ps.disconnect()


if __name__ == "__main__":
    try:
        # ps_calibration(PSCal.ALL)
        # ps_calibration(PSCal.VDC)
        # ps_calibration(PSCal.ADC)
        # ps_calibration(PSCal.VAC)
        ps_calibration(PSCal.AAC)
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
