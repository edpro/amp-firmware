from typing import NamedTuple

from tools.common.logger import LoggedError
from tools.devices.edpro_base import EdproDevice


class PSValues(NamedTuple):
    U: float
    I: float


class EdproPS(EdproDevice):

    def __init__(self):
        super().__init__("ps")
        self.expect_name = "Powersource"
        self.expect_version = "0.30"

    def get_values(self) -> PSValues:
        r = self.request("v")
        if r.get("success") != "1":
            self.logger.throw("Request not succeed!")
        return PSValues(U=float(r["U"]),
                        I=float(r["I"]))

    def set_mode(self, mode: str):
        self.cmd(f"mode {mode}")

    def set_volt(self, v: float):
        level = int(round(v * 10))
        self.cmd(f"set l {level}")

    def set_freq(self, f: int):
        self.cmd(f"set f {f}")


def test():
    device = EdproPS()
    device.connect()
    device.wait_boot_complete()
    device.set_devmode()
    device.get_values()
    device.set_mode("dc")
    device.set_volt(1)


if __name__ == "__main__":
    try:
        test()
    except LoggedError:
        pass
