from typing import NamedTuple

from tools.common.logger import LoggedError
from tools.devices.edpro_base import EdproDevice


class MMValues(NamedTuple):
    mode: str
    rdiv: int
    gain: int
    finit: bool
    value: float


class EdproMM(EdproDevice):

    def __init__(self):
        super().__init__("mm")
        self.expect_name = "Multimeter"
        self.expect_version = "0.37"

    def get_mode(self) -> str:
        response = self.request("mode")
        return response["mode"]

    def get_values(self) -> MMValues:
        r = self.request("v")
        return MMValues(mode=r["mode"],
                        rdiv=int(r["rdiv"]),
                        gain=int(r["gain"]),
                        finit=r["finit"] == '1',
                        value=float(r["value"]))


def test():
    device = EdproMM()
    device.connect()
    device.wait_boot_complete()
    device.get_mode()
    device.get_values()
    device.close()


if __name__ == "__main__":
    try:
        test()
    except LoggedError:
        pass
