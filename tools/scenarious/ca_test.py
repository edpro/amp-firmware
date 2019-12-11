from tools.common.screen import scr_prompt
from tools.common.test import TestReporter, to_amp
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


def devboard_run_test():
    scr_prompt("Disconnect multimeter and powersource from the board!")
    CATest().run()


# noinspection PyMethodParameters
class CATest(Scenario):
    def __init__(self):
        super().__init__("test_ca")

    def on_run(t):
        t.use_edpro_ca()
        t.use_meter()
        t.use_power()
        t.use_generator()

        t.cleanup()
        t.test_all()
        t.cleanup()

    def cleanup(t):
        t.print_task("cleanup")
        t.edpro_ca.set_off()
        t.power.set_volt(1)
        t.generator.set_ac(1, 50)

    def test_all(t):
        t.test_rsel()
        t.test_vgnd()
        t.test_vpow()
        t.test_vpow_rev()
        t.test_vgen()

        """
        multimeter I-COM must be shortet
        """
        # t.test_ipow()
        # t.test_ipow_rev()

    def test_rsel(t):
        t.print_task("Testing 1..10 resistor values")
        t.edpro_ca.set_off()
        r = TestReporter(t.tag)
        data = [
            (1, 10, RigolMode.R_2K),
            (2, 2_000, RigolMode.R_20K),
            (3, 20_000, RigolMode.R_200K),
            (4, 200_000, RigolMode.R_2M),
            (5, 1_800_000, RigolMode.R_2M),
            (6, 10, RigolMode.R_2K),
            (7, 2_000, RigolMode.R_20K),
            (8, 20_000, RigolMode.R_200K),
            (9, 200_000, RigolMode.R_2M),
            (10, 1_800_000, RigolMode.R_2M),
        ]

        for (n, expected, mode) in data:
            t.edpro_ca.set_meas_r(n)
            t.meter.set_mode(mode)

            t.wait(0.25)
            actual = t.meter.measure_r()
            r.trace(f"#{n} expect: {expected}, actual: {actual}")
            r.expect_rel(actual, expected, 0.10)

        r.print_result()
        t.success &= r.success

    def test_vgnd(t):
        t.print_task("Testing mm_vgnd")
        t.edpro_ca.set_off()

        t.meter.set_mode(RigolMode.VDC_2)
        t.edpro_ca.set_mm_vgnd(meas_v=True)

        t.wait(1.0)
        actual = t.meter.measure_vdc()
        t.check_abs(actual, expected=0.0, err=0.0001, msg="Voltage does not match")

    def test_vpow(t):
        t.print_task("Testing VDC Power")
        t.edpro_ca.set_off()

        expected = 3.0
        t.power.set_volt(expected)
        t.meter.set_mode(RigolMode.VDC_20)
        t.edpro_ca.set_mm_vpow(meas_v=True)

        t.wait(1.0)
        actual = t.meter.measure_vdc()
        t.check_rel(actual, expected, err=0.05, msg="Voltage does not match")

    def test_vpow_rev(t):
        t.print_task("Testing VDC Power (reverse)")
        t.edpro_ca.set_off()

        expected = 2.2
        t.meter.set_mode(RigolMode.VDC_20)
        t.power.set_volt(expected)
        t.edpro_ca.set_mm_vpow_rev(meas_v=True)

        t.wait(1.0)
        actual = t.meter.measure_vdc()
        t.check_rel(actual, -expected, err=0.05, msg="Voltage does not match")

    def test_vgen(t):
        t.print_task("Testing Generator voltage")
        t.edpro_ca.set_off()

        expected = 2.0
        t.meter.set_mode(RigolMode.VAC_20)
        t.generator.set_ac(to_amp(expected), 50)
        t.edpro_ca.set_mm_vgen(meas_v=True)

        t.wait(1.0)
        actual = t.meter.measure_vac()
        t.check_rel(actual, expected, err=0.05, msg="Voltage does not match")

    def test_ipow(t):
        t.print_task("Testing ADC Power")
        t.edpro_ca.set_off()

        expected = 0.15
        t.power.set_current(expected)
        t.meter.set_mode(RigolMode.ADC_2A)
        t.edpro_ca.set_mm_ipow(meas_i=True)

        t.wait(1.0)
        actual = t.meter.measure_adc()
        t.check_rel(actual, expected, err=0.05, msg="Current does not match")

    def test_ipow_rev(t):
        t.print_task("Testing ADC Power (reverse)")
        t.edpro_ca.set_off()

        expected = 0.15
        t.power.set_current(expected)
        t.meter.set_mode(RigolMode.ADC_2A)
        t.edpro_ca.set_mm_ipow_rev(meas_i=True)

        t.wait(1.0)
        actual = t.meter.measure_adc()
        t.check_rel(actual, -expected, err=0.05, msg="Current does not match")


if __name__ == "__main__":
    CATest().run()
