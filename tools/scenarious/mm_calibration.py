# noinspection PyMethodParameters
from enum import Flag, auto

from tools.common.test import from_amp, to_amp
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


class MMCalFlags(Flag):
    DC0 = auto()
    VDC = auto()
    ADC = auto()
    AC0 = auto()
    VAC = auto()
    AAC = auto()
    R = auto()
    ANY_AC = AC0 | VAC | AAC
    ANY_DC = DC0 | VDC | ADC


# noinspection PyMethodParameters
class MMCalibration(Scenario):
    save_conf: bool = True

    def __init__(self, flags: MMCalFlags):
        self.flags = flags
        super().__init__("mm_cal")

    def on_run(c):
        c.use_devboard()
        c.use_edpro_mm()
        c.use_meter()
        c.use_power()
        c.use_generator()

        c.generator.set_output_off()

        if bool(c.flags & MMCalFlags.DC0): c._cal_dc0()
        if bool(c.flags & MMCalFlags.VDC): c._cal_vdc()
        if bool(c.flags & MMCalFlags.ADC): c._cal_adc()

        if bool(c.flags & MMCalFlags.AC0): c._cal_ac0()
        if bool(c.flags & MMCalFlags.VAC): c._cal_vac()
        if bool(c.flags & MMCalFlags.AAC): c._cal_aac()

        c.generator.set_output_off()

        if c.save_conf:
            c.edpro_mm.save_conf()

    def _cal_dc0(c):
        c.print_task("calibrate DC0:")
        c.devboard.set_off()

        c.edpro_mm.cmd("mode vdc")
        c.devboard.set_mm_vgnd(meas_v=True)
        c.wait(0.5)
        c.edpro_mm.cmd("cal dc0")

    def _cal_vdc(c):
        c.print_task("calibrate VDC:")
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

        c.wait(1)
        curr = c.meter.measure_adc()
        c.check_abs(curr, 0.16, 0.02, "Cannot set DC current")
        c.edpro_mm.cmd(f"cal adc {curr:0.6f}")

    def _cal_ac0(c):
        c.print_task("calibrate AC0:")
        c.devboard.set_off()

        c.meter.set_mode(RigolMode.VAC_2)
        c.edpro_mm.cmd("mode vac")
        c.devboard.set_mm_vgnd(meas_v=True)
        c.wait(1.0)
        c.edpro_mm.cmd("cal ac0")

    def _cal_vac(c):
        c.print_task("calibrate VAC:")
        c.devboard.set_off()

        freq = 1000
        c.edpro_mm.cmd("mode vac")
        c.meter.set_mode(RigolMode.VAC_2)
        c.devboard.set_mm_vgen(meas_v=True)
        # c.generator.set_load_on(100)
        c.generator.set_output_on()

        # point 1
        expected_v = 0.1
        c.generator.set_ac(to_amp(expected_v), freq)
        c.wait(1.0)
        actual_v = c.meter.measure_vac()
        c.check_rel(actual_v, expected_v, 0.1, "Cannot set AC input")
        c.edpro_mm.cmd(f"cal vac 1 {actual_v:0.6f}")

        # point 2
        expected_v = 1.0
        c.meter.set_mode(RigolMode.VAC_20)
        c.generator.set_ac(to_amp(expected_v), freq)
        c.wait(1.0)
        actual_v = c.meter.measure_vac()
        c.check_rel(actual_v, expected_v, 0.1, "Cannot set AC input")
        c.edpro_mm.cmd(f"cal vac 2 {actual_v:0.6f}")

        # point 3
        expected_v = from_amp(25)  # maximum GENERATOR amplitude
        c.generator.set_ac(to_amp(expected_v), freq)
        c.wait(1.0)
        actual_v = c.meter.measure_vac()
        c.check_rel(actual_v, expected_v, 0.1, "Cannot set AC input")
        c.edpro_mm.cmd(f"cal vac 3 {actual_v:0.6f}")

    def _cal_aac(c):
        c.print_task("calibrate AAC:")
        c.devboard.set_off()

        circuit_r = 60

        freq = 1000
        c.meter.set_mode(RigolMode.AAC_2A)
        c.edpro_mm.cmd("mode aac")
        c.generator.set_output_on()
        c.generator.get_load()
        c.devboard.set_mm_igen(meas_i=True)

        c.logger.info("point 1")
        expected_i = 0.05
        c.generator.set_ac(to_amp(expected_i * circuit_r), freq)
        c.wait(1.0)
        actual_i = c.meter.measure_aac()
        c.check_rel(actual_i, expected_i, 0.1, "Cannot set AC input")
        c.edpro_mm.cmd(f"cal aac 1 {actual_i:0.6f}")

        c.logger.info("point 2")
        expected_i = 0.1
        c.generator.set_ac(to_amp(expected_i * circuit_r), freq)
        c.wait(1.0)
        actual_i = c.meter.measure_aac()
        c.check_rel(actual_i, expected_i, 0.1, "Cannot set AC input")
        c.edpro_mm.cmd(f"cal aac 2 {actual_i:0.6f}")

        c.logger.info("point 3")
        # expected_i = 0.25
        expected_i = 0.14  # for max generator amplitude 25
        c.generator.set_ac(25, freq)
        c.wait(1.0)
        actual_i = c.meter.measure_aac()
        c.check_rel(actual_i, expected_i, 0.1, "Cannot set AC input")
        c.edpro_mm.cmd(f"cal aac 3 {actual_i:0.6f}")


if __name__ == "__main__":
    # test = MMCalibration(MMCalFlags.DC0)
    # test = MMCalibration(MMCalFlags.VDC)
    # test = MMCalibration(MMCalFlags.ADC)

    # test = MMCalibration(MMCalFlags.AC0)
    # test = MMCalibration(MMCalFlags.VAC)
    test = MMCalibration(MMCalFlags.AAC)

    test.save_conf = False
    test.run()
