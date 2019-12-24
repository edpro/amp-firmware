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
        if bool(c.flags & MMCalFlags.ANY_AC):
            c.generator.set_output_off()

        if bool(c.flags & MMCalFlags.R): c._cal_r()

        c.devboard.set_off()

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
        c.check(c.generator.get_load() == "OFF", "Generator load must be 'High Z'")
        c.generator.set_output_on()

        def cal_point(num: int, value: float, mode: RigolMode):
            c.logger.info(f"point {num}")
            expected_v = value
            c.meter.set_mode(mode)
            c.generator.set_ac(to_amp(expected_v), freq)
            c.wait(1.0)
            actual_v = c.meter.measure_vac()
            c.check_rel(actual_v, expected_v, 0.1, "Cannot set AC input")
            c.edpro_mm.cmd(f"cal vac {num} {actual_v:0.6f}")

        cal_point(1, 0.1, RigolMode.VAC_2)
        cal_point(2, 1.0, RigolMode.VAC_2)
        cal_point(3, 4.0, RigolMode.VAC_20)
        cal_point(4, from_amp(25), RigolMode.VAC_20)  # maximum GENERATOR amplitude

    def _cal_aac(c):
        c.print_task("calibrate AAC:")
        c.devboard.set_off()

        owon_max_amplitude = 25
        circuit_max_current = 0.165
        effective_r = owon_max_amplitude / circuit_max_current

        freq = 1000
        c.meter.set_mode(RigolMode.AAC_2A)
        c.edpro_mm.cmd("mode aac")
        c.check(c.generator.get_load() == "OFF", "Generator load must be 'High Z'")
        c.generator.set_output_on()
        c.devboard.set_mm_igen(meas_i=True)

        def cal_point(num: int, value: float):
            c.logger.info(f"point {num}")
            expected_i = value
            c.generator.set_ac(expected_i * effective_r, freq)
            c.wait(1.0)
            actual_i = c.meter.measure_aac()
            c.check_rel(actual_i, expected_i, 0.1, "Cannot set AC input")
            c.edpro_mm.cmd(f"cal aac {num} {actual_i:0.6f}")

        cal_point(1, 0.025)
        cal_point(2, 0.050)
        cal_point(3, 0.100)
        cal_point(4, 0.150)

    def _cal_r(c):
        c.print_task("calibrate R:")
        c.devboard.set_off()
        c.edpro_mm.cmd("mode r")

        # cal rd
        c.logger.info("calibrate R devider")
        c.wait(0.5)
        c.edpro_mm.cmd("cal rd")

        # cal r0
        c.logger.info("calibrate R offset")
        c.devboard.set_mm_rgnd()
        c.wait(0.5)
        c.edpro_mm.cmd("cal r0")

        def cal_range(num: int, rsel: int, r: int, rigol_mode: RigolMode):
            c.logger.info(f"calibrate range {num}")
            c.devboard.set_meas_r(rsel)
            c.meter.set_mode(rigol_mode)
            c.wait(1)
            expected = c.meter.measure_r()
            c.check_rel(expected, r, 0.1, "Cannot set required resistance")
            c.devboard.set_mm_rsel(rsel)
            c.wait(0.5)
            c.edpro_mm.cmd(f"cal r {num} {expected:0.6f}")

        cal_range(1, rsel=2, r=2_000, rigol_mode=RigolMode.R_20K)
        cal_range(2, rsel=3, r=20_000, rigol_mode=RigolMode.R_200K)
        cal_range(3, rsel=4, r=200_000, rigol_mode=RigolMode.R_2M)
        cal_range(4, rsel=5, r=1_800_000, rigol_mode=RigolMode.R_10M)


if __name__ == "__main__":
    # test = MMCalibration(MMCalFlags.DC0)
    # test = MMCalibration(MMCalFlags.VDC)
    # test = MMCalibration(MMCalFlags.ADC)

    # test = MMCalibration(MMCalFlags.AC0)
    test = MMCalibration(MMCalFlags.VAC)
    # test = MMCalibration(MMCalFlags.AAC)

    # test = MMCalibration(MMCalFlags.R)

    # test.save_conf = False
    test.run()
