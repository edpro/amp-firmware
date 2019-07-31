import time

from tools.common.logger import Logger, LoggedError
from tools.edpro_device import EdproPS
from tools.rigol_device import RigolDevice

logger = Logger("ps_cal")

def ps_calibration():
    # init rigol
    rigol = RigolDevice()
    rigol.connect()

    # init powersource
    ps = EdproPS()
    ps.connect()
    ps.wait_boot_complete()
    ps.write("devmode")

    response = ps.ask("i")
    if response.get("name") != "Powersource":
        ps.disconnect()
        logger.throw("Invalid device name!")

    ps.disconnect()

if __name__ == "__main__":
    try:
        ps_calibration()
        input("Press <ENTER> to continue...")
    except LoggedError:
        pass
    except Exception:
        raise
