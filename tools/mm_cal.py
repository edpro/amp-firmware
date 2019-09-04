from typing import Tuple, Optional

from tools.common.logger import Logger, LoggedError
from tools.devices.edpro_device import EdproMM
from tools.devices.rigol_meter import RigolMeter


logger = Logger("mm_cal")


def _init_devices() -> Tuple[EdproMM, RigolMeter]:
    # init rigol
    rigol = RigolMeter()
    rigol.connect()

    # init powersource
    mm = EdproMM()
    mm.connect()
    mm.wait_boot_complete()
    mm.request("devmode")

    # check device is really powersourse
    response = mm.request("i")
    if response.get("name") != "Multimeter":
        logger.throw("Invalid device name!")

    return mm, rigol


def _dispose_devices(ps: Optional[EdproMM], ri: Optional[RigolMeter]):
    if ps: ps.close()
    if ri: ri.close()


def mm_run_calibration():
    mm: Optional[EdproMM] = None
    ri: Optional[RigolMeter] = None

    try:
        mm, ri = _init_devices()
        logger.throw("Not implemented!")
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        _dispose_devices(mm, ri)


def _run():
    mm: Optional[EdproMM] = None
    ri: Optional[RigolMeter] = None
    try:
        mm, ri = _init_devices()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        _dispose_devices(mm, ri)


if __name__ == "__main__":
    _run()
