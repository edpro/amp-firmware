# noinspection PyMethodParameters
from enum import Flag, auto

from tools.common.logger import LoggedError
from tools.common.screen import scr_prompt
from tools.common.test import from_amp, to_amp, erel
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


class MMCalFlags(Flag):
    VDC = auto()
    VAC = auto()
    ADC = auto()
    AAC = auto()
    R = auto()
    ALL = VDC | VAC | ADC | AAC | R


# noinspection PyMethodParameters
class MMCalibration(Scenario):
    def __init__(self, flags: MMCalFlags):
        self.flags = flags
        super().__init__("mm_cal")

    def on_run(c):
        c.use_edpro_mm()
        c.use_meter()
        c.use_power()
        c.use_generator()

        if bool(c.flags & MMCalFlags.VDC):
            c._cal_vdc()

        if bool(c.flags & MMCalFlags.VAC):
            c._cal_vac()

    def _cal_vdc(c):
        is_done: bool = False

        choise = scr_prompt("Short V<->CON wires on multimeter. <Enter> - continue, <s> - skip: ")
        if choise == "":
            is_done = False
            while True:
                try:
                    c._cal_dc0()
                    is_done = True
                    break
                except LoggedError:
                    choise = scr_prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break
                except Exception:
                    raise

        choise = scr_prompt("Connect GENERATOR & RIGOL. <Enter> - continue, <s> - skip: ")
        if choise == "":
            is_done = False
            while True:
                try:
                    c._cal_vdc_values()
                    is_done = True
                    break
                except LoggedError:
                    choise = scr_prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break
                except Exception:
                    raise

        if is_done:
            c.edpro_mm.save_conf()

    def _cal_vac(c):
        is_done: bool = False

        choise = scr_prompt("Short V<->CON wires on multimeter. <Enter> - continue, <s> - skip: ")
        if choise == "":
            is_done = False
            while True:
                try:
                    c._cal_ac0()
                    is_done = True
                    break
                except LoggedError:
                    choise = scr_prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break
                except Exception:
                    raise

        choise = scr_prompt("Connect GENERATOR & RIGOL. <Enter> - continue, <s> - skip: ")
        if choise == "":
            is_done = False
            while True:
                try:
                    c._cal_vac_values()
                    is_done = True
                    break
                except LoggedError:
                    choise = scr_prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break
                except Exception:
                    raise

        if is_done:
            c.edpro_mm.save_conf()

    def _cal_dc0(c):
        c.edpro_mm.cmd("mode dc")
        c.edpro_mm.cmd("cal dc0")

    def _cal_ac0(c):
        c.edpro_mm.cmd("mode ac")
        c.edpro_mm.cmd("cal ac0")

    def _cal_vdc_values(c):
        c.edpro_mm.cmd("mode dc")
        c.meter.set_mode(RigolMode.VDC_2)
        c.power.set_volt(1.0)
        c.wait(1)
        real_v = c.meter.measure_vdc()
        c.check_rel(real_v, 1.0, 0.1, "Cannot set DC volatge 1V")
        c.edpro_mm.cmd(f"cal vdc {real_v:0.6f}")

    def _cal_vac_values(c):
        freq = 1000
        c.edpro_mm.cmd("mode ac")
        c.meter.set_mode(RigolMode.VAC_20)

        # point 1
        expected_v = 0.1
        c.generator.set_ac(to_amp(expected_v), freq)
        c.wait(1.0)
        actual_v = c.meter.measure_vac()
        c.check(erel(expected_v, actual_v) < 0.1, "Expected AC input ~ 0.1V")
        c.edpro_mm.cmd(f"cal vac 1 {actual_v:0.6f}")

        # point 2
        expected_v = 1.0
        c.generator.set_ac(to_amp(expected_v), freq)
        c.wait(1.0)
        actual_v = c.meter.measure_vac()
        c.check(erel(expected_v, actual_v) < 0.1, "Expected AC input ~ 1.0V")
        c.edpro_mm.cmd(f"cal vac 2 {actual_v:0.6f}")

        # point 3
        expected_v = from_amp(25)  # maximum GENERATOR amplitude
        c.generator.set_ac(to_amp(expected_v), freq)
        c.wait(1.0)
        actual_v = c.meter.measure_vac()
        c.check(erel(expected_v, actual_v) < 0.1, "Expected AC input ~ 10V")
        c.edpro_mm.cmd(f"cal vac 3 {actual_v:0.6f}")


if __name__ == "__main__":
    # MMCalibration(MMCalFlags.VDC).run()
    MMCalibration(MMCalFlags.VAC).run()
