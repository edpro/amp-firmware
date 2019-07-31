import usbtmc

from tools.common.logger import LoggedError


class RigolDevice:
    """
    handles communication with RIGOL multimeter
    USB lib: https://github.com/python-ivi/python-usbtmc
    Windows driver: https://zadig.akeo.ie/
    RIGOL Docs: https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DM3058_ProgrammingGuide_EN.pdf
    """

    def __init__(self):
        pass

    def connect(self):
        instr = usbtmc.Instrument(0x1AB1, 0x09C4)
        print(instr.ask("*IDN?"))
        print(instr.ask(":MEASure:VOLTage:DC?"))


def main():
    device = RigolDevice()
    try:
        device.connect()
    except LoggedError:
        pass
    except Exception:
        raise


if __name__ == "__main__":
    main()
