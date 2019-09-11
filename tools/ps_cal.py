import time
from typing import Tuple, Optional

from tools.common.logger import Logger, LoggedError
from tools.common.screen import prompt
from tools.devices.edpro_device import EdproPS
from tools.devices.rigol_meter import RigolMeter, RigolMode

logger = Logger("ps_cal")


def check(val: bool, message: str):
    if not val:
        logger.throw(message)


def _cal_vdc(ps: EdproPS, ri: RigolMeter):
    logger.info("calibrate VDC:")

    ri.set_mode(RigolMode.VDC_20)
    ps.cmd("mode dc")
    ps.cmd("set l 50")
    time.sleep(0.5)

    v = ri.measure_vdc()
    check(4 < v < 6, "Measured value must be about 5V")
    ps.cmd(f"cal vdc {v:0.6f}")
    ps.cmd("set l 0")
    ps.cmd("cal vdcp")


def _cal_vac(ps, ri):
    logger.info("calibrate VAC:")

    ri.set_mode(RigolMode.VAC_20)
    ps.cmd("mode ac")
    ps.cmd("set f 1000")
    ps.cmd("set l 30")
    time.sleep(0.5)

    v = ri.measure_vac()
    check(2 < v < 4, "Measured value must be about 3V")
    ps.cmd(f"cal vac {v:0.6f}")
    ps.cmd("set l 0")
    ps.cmd("cal vacp")


def _cal_adc0(ps):
    logger.info("calibrate ADC zero:")
    ps.cmd("mode dc")
    ps.cmd("set l 0")
    time.sleep(0.5)
    ps.cmd("cal adc0")


def _cal_adc(ps, ri):
    logger.info("calibrate ADC:")

    ri.set_mode(RigolMode.VDC_2)
    ps.cmd("mode dc")
    ps.cmd("set l 10")
    time.sleep(0.5)

    v = ri.measure_vdc()
    check(0.1 < v < 0.2, "Measured value must be about 0.15A")
    ps.cmd(f"cal adc {v:0.6f}")


def _cal_aac0(ps):
    logger.info("calibrate AAC zero:")
    ps.cmd("mode ac")
    ps.cmd("set f 1000")
    ps.cmd("set l 0")
    time.sleep(1)
    ps.cmd("cal aac0")


def _cal_aac(ps, ri):
    logger.info("calibrate AAC:")

    ri.set_mode(RigolMode.VAC_2)
    ps.cmd("mode ac")
    ps.cmd("set f 1000")
    ps.cmd("set l 10")

    time.sleep(1)
    v = ri.measure_vac()
    check(0.1 < v < 0.2, "Measured value must be about 0.15A")
    ps.cmd(f"cal aac {v:0.6f}")


def _init_devices() -> Tuple[EdproPS, RigolMeter]:
    # init rigol
    rigol = RigolMeter()
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


def _dispose_devices(ps: Optional[EdproPS], ri: Optional[RigolMeter]):
    if ps: ps.close()
    if ri: ri.close()


def ps_run_calibration():
    ps: Optional[EdproPS] = None
    ri: Optional[RigolMeter] = None

    try:
        ps, ri = _init_devices()
        is_done = False

        choise = prompt("Connect Rigol to Powersource output. <Enter> - continue, <s> - skip: ")

        if choise == "":
            while True:
                try:
                    _cal_vdc(ps, ri)
                    _cal_adc0(ps)
                    _cal_vac(ps, ri)
                    _cal_aac0(ps)
                    is_done = True
                    break
                except LoggedError:
                    choise = prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break
                except Exception:
                    raise

        choise = prompt("Connect Rigol to 1Ω resistor. <Enter> - continue, <s> - skip: ")

        if choise == "":
            while True:
                try:
                    _cal_adc(ps, ri)
                    _cal_aac(ps, ri)
                    is_done = True
                    break
                except LoggedError:
                    choise = prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break
                except Exception:
                    raise

        if is_done:
            ps.save_conf()
            logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        _dispose_devices(ps, ri)


def _run():
    ps: Optional[EdproPS] = None
    ri: Optional[RigolMeter] = None
    try:
        ps, ri = _init_devices()
        _cal_adc0(ps)
        _cal_aac0(ps)
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        _dispose_devices(ps, ri)


if __name__ == "__main__":
    _run()
