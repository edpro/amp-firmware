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
        c.use_devboard()
        c.use_edpro_mm()
        c.use_meter()
        c.use_power()
        c.use_generator()

        if bool(c.flags & MMCalFlags.VDC):
            c._cal_vdc()

        if bool(c.flags & MMCalFlags.ADC):
            c._cal_adc()

        #
        # if bool(c.flags & MMCalFlags.VAC):
        #     c._cal_vac()

        c.edpro_mm.save_conf()

    def _cal_vdc(c):
        c.print_task("calibrate VDC:")
        c.devboard.set_off()

        """ cal dc0  """
        c.meter.set_mode(RigolMode.VDC_2)
        c.edpro_mm.cmd("mode vdc")
        c.wait(1)
        c.devboard.set_mm_vgnd()
        c.edpro_mm.cmd("cal dc0")

        """ cal vdc  """
        c.devboard.set_off()
        c.power.set_volt(1.0)
        c.devboard.set_mm_vpow(meas_v=True)
        c.wait(1)
        volt = c.meter.measure_vdc()
        c.check_abs(volt, 1.0, 0.1, "Cannot set DC voltage")
        c.edpro_mm.cmd(f"cal vdc {volt:0.6f}")

    def _cal_adc(c):
        c.print_task("calibrate ADC:")
        c.devboard.set_off()
        c.power.set_volt(4)
        c.wait(1)

        c.meter.set_mode(RigolMode.ADC_2A)
        c.power.set_current(0.16)
        c.edpro_mm.cmd("mode adc")
        c.devboard.set_mm_ipow(meas_i=True)
        # c.devboard.set_mm_ipow()
        # c.devboard.set_mm_ipow2(meas_i=True)
        # c.devboard.set_mm_ipow2()

        c.wait(1)
        curr = c.meter.measure_adc()
        c.check_abs(curr, 0.16, 0.02, "Cannot set DC current")
        c.edpro_mm.cmd(f"cal adc {curr:0.6f}")

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

    def _cal_ac0(c):
        c.edpro_mm.cmd("mode ac")
        c.edpro_mm.cmd("cal ac0")

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
    MMCalibration(MMCalFlags.ADC).run()
    # MMCalibration(MMCalFlags.VAC).run()
