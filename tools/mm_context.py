import time

from tools.common.logger import LoggedError
from tools.devices.edpro_device import EdproMM
from tools.devices.owon_generator import OwonGenerator
from tools.devices.owon_power import OwonPower
from tools.devices.rigol_meter import RigolMeter


class MMContext:
    def __init__(self):
        self.mm: EdproMM = EdproMM()
        self.gen: OwonGenerator = OwonGenerator()
        self.power: OwonPower = OwonPower()
        self.meter: RigolMeter = RigolMeter()

    def init(self):
        self.mm.connect()
        self.mm.wait_boot_complete()
        self.mm.request("devmode")

        self.meter.connect()
        self.power.connect()
        self.gen.connect()

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
    except:
        raise
    finally:
        c.dispose()

if __name__ == "__main__":
    run_test()
