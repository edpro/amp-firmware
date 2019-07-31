from tools.common.logger import Logger, LoggedError
from tools.edpro_device import EdproPS
from tools.rigol_device import RigolDevice

logger = Logger("ps_cal")

def ps_calibration():
    # init rigol
    rigol = RigolDevice()

    # init powersource
    ps_device = EdproPS()
    ps_device.connect()
    ps_device.wait_boot_complete()
    response = ps_device.run_request("i")
    if response.get("name") != "Powersource":
        ps_device.disconnect()
        logger.throw("Invalid device name!")


if __name__ == "__main__":
    try:
        ps_calibration()
    except LoggedError:
        pass
    except Exception:
        raise
