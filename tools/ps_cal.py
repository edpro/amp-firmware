from tools.common.logger import Logger, LoggerException
from tools.edpro_device import EdproPS

logger = Logger("ps_cal")

def ps_calibration():
    ps_device = EdproPS()
    ps_device.connect()
    ps_device.wait_boot_complete()
    response = ps_device.run_request("i")
    if response.get("name") != "Powersource":
        logger.throw("Invalid device name!")
    ps_device.disconnect()

if __name__ == "__main__":
    try:
        ps_calibration()
    except LoggerException:
        pass
    except Exception:
        raise
