import time

import pyvisa
from pyvisa.resources import USBInstrument

from tools.common.logger import LoggedError, Logger

logger = Logger("ri_load")

rm = pyvisa.ResourceManager()


# noinspection PyPep8Naming
class RigolLoad:
    """
    handles communication with RIGOL DC load
    Python USB lib: https://github.com/python-ivi/python-usbtmc
    Windows driver: install Ultra Sigma from www.rigol.eu
    Manual: https://www.batronix.com/files/Rigol/Elektronische-Lasten/DL3000/DL3000_ProgrammingManual_EN.pdf
    """

    _device: USBInstrument = None

    def __init__(self):
        pass

    def connect(self):
        logger.info("connect")
        try:
            # self._device = usbtmc.Instrument(0x1AB1, 0x0E11)
            # noinspection PyTypeChecker
            self._device = rm.open_resource('USB0::0x1AB1::0x0E11::DL3B203700184::INSTR')
        except Exception as e:
            logger.throw(str(e))
        self._ask("*IDN?")

    def reset(self):
        self._write("*RST")
        self.wait()

    def wait(self):
        self._write("*WAI")

    def close(self):
        logger.info("disconnect")
        if self._device:
            self._device.close()

    def _write(self, cmd: str):
        logger.trace(f"<- {cmd}")
        try:
            self._device.write(cmd)
        except Exception as e:
            logger.throw(e)

    def _ask(self, cmd: str) -> str:
        logger.trace(f"<- {cmd}")
        response = ""
        try:
            response = self._device.query(cmd)
            logger.trace(f"-> {response}")
        except Exception as e:
            logger.throw(e)

        return response

    def measure_voltage(self) -> float:
        response = self._ask(":MEASure:VOLTage?")
        return float(response)

    def measure_current(self) -> float:
        response = self._ask(":MEASure:CURRent?")
        return float(response)

    def measure_current_max(self) -> float:
        response = self._ask(":MEASure:CURRent:MAX?")
        return float(response)

    def set_pulse_current(self, value: float, width_ms: float):
        self._write(f":SOURce:CURRent:TRANsient:MODE PULSe")
        self._write(f":SOURce:CURRent:TRANsient:ALEVel {value}")
        self._write(f":SOURce:CURRent:TRANsient:BLEVel {0.0}")
        self._write(f":SOURce:CURRent:TRANsient:AWIDth {width_ms}")
        self._write(f":SOURce:CURRent:TRANsient:BWIDth {width_ms}")
        self._write(f":SOURce:CURRent:SLEW:POS {1.0}")
        self._write(f":SOURce:CURRent:SLEW:NEG {1.0}")
        self._write(":TRIGger:SOURce BUS")

    def trigger(self):
        self._write(":TRIGger")
        self.wait()

    def set_const_current(self, value: float):
        self._write(f":SOURce:FUNCtion CURRent")
        self._write(f":SOURce:CURRent {value}")

    def get_func(self) -> str:
        return self._ask(":SOURce:FUNCtion?")

    def set_input(self, isOn: int):
        self._write(f":SOURce:INPut {isOn}")
        self.wait()

    def check_error(self):
        self._ask(":SYSTem:ERRor?")


def test():
    device = RigolLoad()
    try:
        device.connect()
        device.reset()

        # device.measure_voltage()
        # device.measure_current()

        # device.set_const_current(0.1)
        # device.get_func()
        # device.set_input(1)
        # time.sleep(1.0)
        # device.measure_voltage()
        # device.measure_current()
        # device.set_input(0)

        device.set_pulse_current(value=5, width_ms=0.03)
        # device.set_pulse_current(value=3, width_ms=5)
        device.trigger()
        time.sleep(0.1)
        device.measure_current_max()
        device.set_input(isOn=0)

    except LoggedError:
        pass
    finally:
        device.close()


if __name__ == "__main__":
    test()
