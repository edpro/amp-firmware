from tools.common.test import TestReporter, to_amp
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


# noinspection PyMethodParameters
class CATestAll(Scenario):
    def __init__(self):
        super().__init__("test_ca")

    def on_run(t):
        t.use_edpro_ca()
        t.use_meter()
        t.use_power()
        t.use_generator()

        # t.edpro_ca.set_off()

        # t.test_rsel()
        t.test_vpow()
        # t.test_vpow_rev()
        # t.test_vgen()

        t.edpro_ca.set_off()

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
            actual = t.meter.measure_r()
            r.trace(f"#{n} expect: {expected}, actual: {actual}")
            r.expect_rel(actual, expected, 0.1)

        r.print_result()
        t.success &= r.success

    def test_vpow(t):
        t.print_task("Testing VDC Power")
        t.edpro_ca.set_off()
        t.power.set_volt(3.0)
        t.meter.set_mode(RigolMode.VDC_20)
        t.edpro_ca.set_mm_vpow(meas_v=True)
        t.wait(0.25)
        actual = t.meter.measure_vdc()
        t.check_rel(actual, expected=3.0, err=0.01, msg="Voltage does not match")
        t.power.set_volt(0)

    def test_vpow_rev(t):
        t.print_task("Testing VDC Power (reverse)")
        t.edpro_ca.set_off()
        t.meter.set_mode(RigolMode.VDC_20)
        t.power.set_volt(2)
        t.edpro_ca.set_mm_vpow(meas_v=True)
        actual = t.meter.measure_vdc()
        t.check_rel(actual, expected=-2, err=0.01, msg="Voltage does not match")

    def test_vgen(t):
        t.print_task("Testing VAC Generator")
        t.edpro_ca.set_off()
        t.meter.set_mode(RigolMode.VAC_20)
        t.generator.set_load_on(100)
        t.generator.set_ac(to_amp(2), 100)
        t.edpro_ca.set_mm_vgen(meas_v=True)
        actual = t.meter.measure_vac()
        t.check_rel(actual, expected=2, err=0.01, msg="Voltage does not match")


if __name__ == "__main__":
    CATestAll().run()
