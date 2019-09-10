import time

from tools.common.logger import LoggedError, Logger
from tools.common.screen import Colors
from tools.devices.edpro_device import EdproMM, EdproPS
from tools.devices.owon_generator import OwonGenerator
from tools.devices.owon_power import OwonPower
from tools.devices.rigol_meter import RigolMeter


class Scenario:

    def __init__(self, tag: str):
        self.tag: str = tag
        self.logger: Logger = Logger(tag)

        self.edpro_mm: EdproMM = EdproMM()
        self.edpro_ps: EdproPS = EdproPS()
        self.meter: RigolMeter = RigolMeter()
        self.generator: OwonGenerator = OwonGenerator()
        self.power: OwonPower = OwonPower()

        self._edpro_mm_used: bool = False
        self._edpro_ps_used: bool = False
        self._meter_used: bool = False
        self._power_used: bool = False
        self._generator_used: bool = False

    def init_edpro_mm(self):
        self._edpro_mm_used = True
        self.edpro_mm.connect()
        self.edpro_mm.wait_boot_complete()
        self.edpro_mm.request("devmode")
        info = self.edpro_mm.request_info()
        self.check_str(info.name, "Multimeter", "Invalid device name!")

    def init_edpro_ps(self):
        self._edpro_ps_used = True
        self.edpro_ps.connect()
        self.edpro_ps.wait_boot_complete()
        self.edpro_ps.request("devmode")
        info = self.edpro_ps.request_info()
        self.check_str(info.name, "Powersource", "Invalid device name!")

    def init_power(self):
        self._power_used = True
        self.power.connect()

    def init_meter(self):
        self._meter_used = True
        self.meter.connect()

    def init_generator(self):
        self._generator_used = True
        self.generator.connect()

    def fail(self, msg: str):
        self.logger.throw(msg)

    def check(self, condition: bool, msg: str):
        if not condition:
            self.fail(msg)

    def check_str(self, actual: str, expected: str, msg: str):
        if expected == actual:
            return
        err_msg = f'{msg}\n'
        err_msg += f'    expected : "{expected}"\n'
        err_msg += f'    actual   : "{actual}"'
        self.logger.throw(err_msg)

    def wait(self, seconds: int):
        time.sleep(seconds)

    def on_run(self):
        pass

    def _dispose(self):
        if self._edpro_mm_used:
            self.edpro_mm.close()
        if self._edpro_ps_used:
            self.edpro_ps.close()
        if self._meter_used:
            self.meter.close()
        if self._power_used:
            self.power.close()
        if self._generator_used:
            self.generator.close()

    def run(self):
        success = False
        self.logger.print(Colors.GREEN, "begin")
        try:
            self.on_run()
            success = True
        except LoggedError:
            pass
        except Exception:
            raise
        finally:
            self._dispose()
        if success:
            self.logger.print(Colors.GREEN, "OK")
        else:
            self.logger.print(Colors.LIGHT_RED, "Scenario FAILED")


class _TestScenario_(Scenario):
    def __init__(self):
        super().__init__("test")

    def on_run(self):
        # self.init_edpro_mm()
        self.init_edpro_ps()


if __name__ == "__main__":
    _TestScenario_().run()
