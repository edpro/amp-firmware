from tools.common.logger import Logger, LoggerException
from tools.edpro_device import EdproPS

logger = Logger("ps_cal")

def ps_calibration():
    ps_device = EdproPS()
    try:
        ps_device.connect()
        response = ps_device.run_request("i")
    except LoggerException:
        pass
    except Exception:
        raise

    ps_device.disconnect()

if __name__ == "__main__":
    ps_calibration()
