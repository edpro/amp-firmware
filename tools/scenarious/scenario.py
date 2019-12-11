import time
from typing import Optional

from tools.common.logger import LoggedError, Logger
from tools.common.screen import Colors
from tools.common.test import erel, rel_str, eabs
from tools.devices.edpro_db import EdproDevBoard
from tools.devices.edpro_mm import EdproMM
from tools.devices.edpro_ps import EdproPS
from tools.devices.owon_generator import OwonGenerator
from tools.devices.owon_power import OwonPower
from tools.devices.rigol_meter import RigolMeter


class Scenario:
    edpro_mm: Optional[EdproMM] = None
    edpro_ps: Optional[EdproPS] = None
    devboard: Optional[EdproDevBoard] = None
    meter: Optional[RigolMeter] = None
    generator: Optional[OwonGenerator] = None
    power: Optional[OwonPower] = None

    def __init__(self, tag: str):
        self.tag: str = tag
        self.logger: Logger = Logger(tag)
        self.success: bool = True

    def use_edpro_ca(self):
        self.devboard = EdproDevBoard()
        self.devboard.connect()
        self.devboard.wait_boot_complete()
        info = self.devboard.get_info()
        self.check_str(info.name, "Calibrator", "Invalid device name!")

    def use_edpro_mm(self):
        self.edpro_mm = EdproMM()
        self.edpro_mm.connect()
        self.edpro_mm.wait_boot_complete()
        self.edpro_mm.set_devmode()
        info = self.edpro_mm.get_info()
        self.check_str(info.name, "Multimeter", "Invalid device name!")

    def use_edpro_ps(self):
        self.edpro_ps = EdproPS()
        self.edpro_ps.connect()
        self.edpro_ps.wait_boot_complete()
        self.edpro_ps.set_devmode()
        info = self.edpro_ps.get_info()
        self.check_str(info.name, "Powersource", "Invalid device name!")

    def use_power(self):
        self.power = OwonPower()
        self.power.connect()

    def use_meter(self):
        self.meter = RigolMeter()
        self.meter.connect()

    def use_generator(self):
        self.generator = OwonGenerator()
        self.generator.connect()
        self.generator.set_output_on()
        self.generator.set_load_on(100)

    def fail(self, msg: str):
        self.logger.throw(msg)

    def check(self, condition: bool, msg: str):
        if not condition:
            self.fail(msg)

    def print_task(self, text: str):
        self.logger.print(Colors.GREEN, "#" )
        self.logger.print(Colors.GREEN, "# " + text)
        self.logger.print(Colors.GREEN, "#")

    def check_str(self, actual: str, expected: str, msg: str):
        if expected == actual:
            return
        err_msg = f'{msg}\n'
        err_msg += f'    expected : "{expected}"\n'
        err_msg += f'    actual   : "{actual}"'
        self.logger.throw(err_msg)

    def check_rel(self, actual: float, expected: float, err: float, msg: str):
        e = erel(actual, expected)
        if e <= err:
            return
        err_msg = f'{msg}\n'
        err_msg += f'\texpected : {expected} +- {rel_str(err)}\n'
        err_msg += f'\tactual   : {actual}'
        self.logger.throw(err_msg)

    def check_abs(self, actual: float, expected: float, err: float, msg: str):
        e = eabs(actual, expected)
        if e <= err:
            return
        err_msg = f'{msg}\n'
        err_msg += f'\texpected : {expected} +- {err}\n'
        err_msg += f'\tactual   : {actual}'
        self.logger.throw(err_msg)

    @staticmethod
    def wait(seconds: float):
        time.sleep(seconds)

    def on_run(self):
        pass

    def _dispose(self):
        if (self.edpro_mm):
            self.edpro_mm.close()
        if (self.edpro_ps):
            self.edpro_ps.close()
        if (self.devboard):
            self.devboard.close()
        if (self.meter):
            self.meter.close()
        if (self.power):
            self.power.close()
        if (self.generator):
            self.generator.close()

    def run(self):
        self.logger.print(Colors.GREEN, "begin")

        try:
            self.on_run()
        except LoggedError:
            self.success = False
            pass
        except Exception:
            self.success = False
            raise
        finally:
            self._dispose()

        if self.success:
            self.logger.print(Colors.GREEN, "===")
            self.logger.print(Colors.GREEN, "OK!")
            self.logger.print(Colors.GREEN, "===")
        else:
            self.logger.print(Colors.LIGHT_RED, "======")
            self.logger.print(Colors.LIGHT_RED, "FAILED")
            self.logger.print(Colors.LIGHT_RED, "======")


class TestScenario(Scenario):
    def __init__(self):
        super().__init__("test")

    def on_run(self):
        # self.init_edpro_mm()
        self.use_edpro_ps()


if __name__ == "__main__":
    TestScenario().run()
