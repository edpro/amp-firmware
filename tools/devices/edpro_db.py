from tools.common.esp import UartStr
from tools.common.logger import LoggedError
from tools.devices.edpro_base import EdproDevice


class EdproDevBoard(EdproDevice):
    def __init__(self):
        super().__init__("db")
        self.uart_str = UartStr.CH340
        self.expect_name = "Calibrator"
        self.expect_version = "0.1"

    def set_off(self):
        self.cmd("set off")

    def set_mm_vgen(self, meas_v: bool = False):
        cmd = "set mm_vgen"
        if (meas_v): cmd += " meas_v"
        self.cmd(cmd)

    def set_mm_vpow(self, meas_v: bool = False):
        cmd = "set mm_vpow"
        if (meas_v): cmd += " meas_v"
        self.cmd(cmd)

    def set_mm_vpow_rev(self, meas_v: bool = False):
        cmd = "set mm_vpow_rev"
        if (meas_v): cmd += " meas_v"
        self.cmd(cmd)

    def set_mm_vgnd(self, meas_v: bool = False):
        cmd = "set mm_vgnd"
        if (meas_v): cmd += " meas_v"
        self.cmd(cmd)

    def set_mm_igen(self, meas_i: bool = False):
        cmd = "set mm_igen"
        if (meas_i): cmd += " meas_i"
        self.cmd(cmd)

    def set_mm_ipow(self, meas_i: bool = False):
        cmd = "set mm_ipow"
        if (meas_i): cmd += " meas_i"
        self.cmd(cmd)

    def set_mm_ipow_rev(self, meas_i: bool = False):
        cmd = "set mm_ipow_rev"
        if (meas_i): cmd += " meas_i"
        self.cmd(cmd)

    def set_mm_rgnd(self):
        self.cmd("set mm_rgnd")

    def set_mm_rsel(self, n1: int, n2: int = None, n3: int = None):
        cmd = f"set mm_rsel {n1}"
        if n2 is not None: cmd += f" {n2}"
        if n3 is not None: cmd += f" {n3}"
        self.cmd(cmd)

    def set_pp_load(self, n: int, meas_i: bool = False, meas_v: bool = False):
        cmd = f"set pp_load {n}"
        if (meas_i): cmd += " meas_i"
        if (meas_v): cmd += " meas_v"
        self.cmd(cmd)

    def set_meas_v(self):
        self.cmd("set meas_v")

    def set_meas_i(self):
        self.cmd("set meas_i")

    def set_meas_r(self, n1: int, n2: int = None, n3: int = None):
        cmd = f"set meas_r {n1}"
        if n2 is not None: cmd += f" {n2}"
        if n3 is not None: cmd += f" {n3}"
        self.cmd(cmd)


def test():
    device = EdproDevBoard()
    device.connect()
    device.wait_boot_complete()


if __name__ == "__main__":
    try:
        test()
    except LoggedError:
        pass
