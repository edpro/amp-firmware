from enum import Enum
from typing import Optional

import usbtmc

from tools.common.logger import LoggedError, Logger

logger = Logger("rigol")


class RigolMode(Enum):
    VDC_2 = ":MEASure:VOLTage:DC 1"
    VDC_20 = ":MEASure:VOLTage:DC 2"
    VAC_2 = ":MEASure:VOLTage:AC 1"
    VAC_20 = ":MEASure:VOLTage:AC 2"
    FREQ_20 = ":MEASure:FREQuency 2"


# noinspection PyPep8Naming
class RigolDevice:
    """
    handles communication with RIGOL multimeter
    USB lib: https://github.com/python-ivi/python-usbtmc
    Windows driver: https://zadig.akeo.ie/
    RIGOL Docs: https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DM3058_ProgrammingGuide_EN.pdf
    """

    def __init__(self):
        self.device: Optional[usbtmc.Instrument] = None

    def connect(self):
        logger.info("connect")
        try:
            self.device = usbtmc.Instrument(0x1AB1, 0x09C4)
        except Exception as e:
            logger.throw(str(e))
        self._ask("*IDN?")

    def close(self):
        if self.device:
            self.device.close()

    def _write(self, cmd: str):
        logger.trace(f"<- {cmd}")
        try:
            self.device.write(cmd)
        except Exception as e:
            logger.throw(e)

    def _ask(self, cmd: str) -> str:
        logger.trace(f"<- {cmd}")
        response = ""
        try:
            response = self.device.ask(cmd)
            logger.trace(f"-> {response}")
        except Exception as e:
            logger.throw(e)

        return response

    def mode(self, mode: RigolMode):
        self._write(mode.value)

    def measure_vdc(self) -> float:
        response = self._ask(":MEASure:VOLTage:DC?")
        return float(response)

    def measure_vac(self) -> float:
        response = self._ask(":MEASure:VOLTage:AC?")
        return float(response)

    def measure_freq(self) -> float:
        response = self._ask(":MEASure:FREQuency?")
        return float(response)

def test():
    device = RigolDevice()
    device.connect()
    device.mode(RigolMode.VDC_20)
    device.measure_vdc()


if __name__ == "__main__":
    try:
        test()
    except LoggedError:
        pass
    except Exception:
        raise
