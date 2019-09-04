import time

from tools.common.logger import LoggedError, Logger
from tools.devices.edpro_device import EdproPS
from tools.devices.owon_generator import OwonGenerator
from tools.devices.owon_power import OwonPower
from tools.devices.rigol_meter import RigolMeter

logger = Logger("ps_context")


class PSContext:
    def __init__(self):
        self.ps: EdproPS = EdproPS()
        self.gen: OwonGenerator = OwonGenerator()
        self.power: OwonPower = OwonPower()
        self.meter: RigolMeter = RigolMeter()

    def init(self):
        self.meter.connect()
        self.power.connect()
        self.gen.connect()

        self.ps.connect()
        self.ps.wait_boot_complete()
        self.ps.request("devmode")
        # check device is really powersourse
        response = self.ps.request("i")
        if response.get("name") != "Powersource":
            logger.throw("Invalid device name!")

    def dispose(self):
        self.ps.close()
        self.meter.close()
        self.power.close()
        self.gen.close()


def run_test():
    c = PSContext()
    try:
        c.init()
        time.sleep(1)
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        c.dispose()


if __name__ == "__main__":
    run_test()
