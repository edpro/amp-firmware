from tools.common.logger import LoggedError
from tools.common.screen import scr_prompt
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


# noinspection PyMethodParameters
class PSCalibration(Scenario):
    def __init__(self):
        super().__init__("ps_cal")

    def on_run(c):
        c.use_edpro_ps()
        c.use_meter()

        choise = scr_prompt("Connect Rigol to Powersource output. <Enter> - continue, <s> - skip: ")
        if choise == "":
            while True:
                try:
                    c._cal_vdc()
                    c._cal_adc0()
                    c._cal_vac()
                    c._cal_aac0()
                    c.edpro_ps.save_conf()
                    break
                except LoggedError:
                    choise = scr_prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break

        choise = scr_prompt("Connect Rigol to 1Ω resistor. <Enter> - continue, <s> - skip: ")

        if choise == "":
            while True:
                try:
                    c._cal_adc()
                    c._cal_aac()
                    c.edpro_ps.save_conf()
                    break
                except LoggedError:
                    choise = scr_prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break

    def _cal_vdc(c):
        c.logger.info("calibrate VDC:")

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
        c.logger.info("calibrate VAC:")

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
        c.logger.info("calibrate ADC zero:")
        c.edpro_ps.cmd("mode dc")
        c.edpro_ps.cmd("set l 0")
        c.wait(0.5)
        c.edpro_ps.cmd("cal adc0")

    def _cal_adc(c):
        c.logger.info("calibrate ADC:")

        c.meter.set_mode(RigolMode.VDC_2)
        c.edpro_ps.cmd("mode dc")
        c.edpro_ps.cmd("set l 10")
        c.wait(0.5)

        v = c.meter.measure_vdc()
        c.check(0.1 < v < 0.2, "Measured value must be about 0.15A")
        c.edpro_ps.cmd(f"cal adc {v:0.6f}")

    def _cal_aac0(c):
        c.logger.info("calibrate AAC zero:")
        c.edpro_ps.cmd("mode ac")
        c.edpro_ps.cmd("set f 1000")
        c.edpro_ps.cmd("set l 0")
        c.wait(1)
        c.edpro_ps.cmd("cal aac0")

    def _cal_aac(c):
        c.logger.info("calibrate AAC:")

        c.meter.set_mode(RigolMode.VAC_2)
        c.edpro_ps.cmd("mode ac")
        c.edpro_ps.cmd("set f 1000")
        c.edpro_ps.cmd("set l 10")

        c.wait(1)
        v = c.meter.measure_vac()
        c.check(0.1 < v < 0.2, "Measured value must be about 0.15A")
        c.edpro_ps.cmd(f"cal aac {v:0.6f}")


if __name__ == "__main__":
    PSCalibration().run()
