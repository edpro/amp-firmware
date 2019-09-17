import time

from tools.common.logger import Logger, LoggedError
from tools.devices.edpro_mm import EdproMM
from tools.devices.owon_generator import OwonGenerator
from tools.devices.owon_power import OwonPower
from tools.devices.rigol_meter import RigolMeter

logger = Logger("mm_context")


class MMContext:
    def __init__(self):
        self.mm: EdproMM = EdproMM()
        self.gen: OwonGenerator = OwonGenerator()
        self.power: OwonPower = OwonPower()
        self.meter: RigolMeter = RigolMeter()

    def init(self):
        self.meter.connect()
        self.power.connect()
        self.gen.connect()

        self.mm.connect()
        self.mm.wait_boot_complete()
        self.mm.request("devmode")
        # check device is really powersourse
        response = self.mm.request("i")
        if response.get("name") != "Multimeter":
            logger.throw("Invalid device name!")

    def dispose(self):
        self.mm.close()
        self.meter.close()
        self.power.close()
        self.gen.close()


def run_test():
    c = MMContext()
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
