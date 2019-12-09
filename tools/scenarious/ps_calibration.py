from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


# noinspection PyMethodParameters
class PSCalibration(Scenario):
    def __init__(self):
        super().__init__("ps_cal")

    def on_run(c):
        c.use_edpro_ca()
        c.use_edpro_ps()
        c.use_meter()

        # VOLTAGE
        c.edpro_ps.cmd("mode dc")
        c.edpro_ps.cmd("set l 0")
        c.edpro_ca.set_meas_v()
        c._cal_vdc()
        c._cal_vac()
        c._cal_adc0()
        c._cal_aac0()
        c.edpro_ps.save_conf()

        # CURRENT
        c._cal_adc()
        c._cal_aac()
        c.edpro_ps.save_conf()

        c.edpro_ca.set_off()

    def _cal_vdc(c):
        c.print_task("calibrate VDC:")

        c.meter.set_mode(RigolMode.VDC_20)
        c.edpro_ps.cmd("mode dc")
        c.edpro_ps.cmd("set l 50")
        c.wait(0.5)

        v = c.meter.measure_vdc()
        c.check(2.5 < v < 6, "Measured value must be about 5V")
        c.edpro_ps.cmd(f"cal vdc {v:0.6f}")
        c.edpro_ps.cmd("set l 0")
        c.edpro_ps.cmd("cal vdcp")

    def _cal_vac(c):
        c.print_task("calibrate VAC:")

        c.meter.set_mode(RigolMode.VAC_20)
        c.edpro_ps.cmd("mode ac")
        c.edpro_ps.cmd("set f 1000")
        c.edpro_ps.cmd("set l 30")
        c.wait(0.5)

        v = c.meter.measure_vac()
        c.check(1.5 < v < 4, "Measured value must be about 3V")
        c.edpro_ps.cmd(f"cal vac {v:0.6f}")
        c.edpro_ps.cmd("set l 0")
        c.edpro_ps.cmd("cal vacp")

    def _cal_adc0(c):
        c.print_task("calibrate ADC zero:")
        c.edpro_ps.cmd("mode dc")
        c.edpro_ps.cmd("set l 0")
        c.wait(0.5)
        c.edpro_ps.cmd("cal adc0")

    def _cal_adc(c):
        c.print_task("calibrate ADC:")
        c.edpro_ca.set_off()

        c.meter.set_mode(RigolMode.ADC_2A)
        c.edpro_ps.cmd("mode dc")
        c.edpro_ps.cmd("set l 15")
        c.edpro_ca.set_pp_load(1, meas_i=True)

        c.wait(0.5)
        actual = -c.meter.measure_adc()
        c.check(0.1 < actual < 0.3, "Measured value must be in range 0.1...0.3A")
        c.edpro_ps.cmd(f"cal adc {actual:0.6f}")

    def _cal_aac0(c):
        c.print_task("calibrate AAC zero:")
        c.edpro_ps.cmd("mode ac")
        c.edpro_ps.cmd("set f 1000")
        c.edpro_ps.cmd("set l 0")
        c.wait(1)
        c.edpro_ps.cmd("cal aac0")

    def _cal_aac(c):
        c.print_task("calibrate AAC:")
        c.edpro_ca.set_off()

        c.meter.set_mode(RigolMode.AAC_2A)
        c.edpro_ps.cmd("mode ac")
        c.edpro_ps.cmd("set f 1000")
        c.edpro_ps.cmd("set l 15")
        c.edpro_ca.set_pp_load(1, meas_i=True)

        c.wait(1)
        actual = c.meter.measure_aac()
        c.check(0.1 < actual < 0.2, "Measured value must be about 0.15A")
        c.edpro_ps.cmd(f"cal aac {actual:0.6f}")


if __name__ == "__main__":
    PSCalibration().run()
