from tools.common.test import TestReporter
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario

LOAD_R = 4.7
PS_R = 1


# noinspection PyMethodParameters
class PSTestLoadDC(Scenario):
    def __init__(self):
        super().__init__("test_load")

    def on_run(t):
        t.use_devboard()
        t.use_edpro_ps()
        t.use_meter()

        t.test_load_dc()
        t.test_load_short()

    def test_load_short(t):
        t.print_task("test_load_short")
        t.devboard.set_off()
        t.edpro_ps.set_mode("dc")
        t.edpro_ps.set_volt(5)
        t.wait(0.5)
        initial = t.edpro_ps.get_values()
        t.check_abs(initial.U, 5, 0.1, "Cannot set requiret voltage")

        t.devboard.set_pp_load(0)
        t.wait(1)
        t.devboard.set_off()
        after = t.edpro_ps.get_values()
        t.check_abs(after.U, initial.U, 0.01, "Voltage is not restored after shorting")

    def test_load_dc(t):
        t.print_task("test_load_dc")
        t.devboard.set_off()
        t.edpro_ps.set_mode("dc")
        t.edpro_ps.set_volt(0)
        t.meter.set_mode(RigolMode.VDC_20)

        reporter = TestReporter(t.tag)

        for volt in [0.2, 0.4, 0.8, 2, 4, 5]:
            t.edpro_ps.set_volt(volt)
            t.wait(0.5)
            initial_values = t.edpro_ps.get_values()
            t.check_abs(initial_values.U, volt, 0.1, "Cannot set required voltage")

            t.devboard.set_pp_load(2)
            t.wait(1.0)
            load_values = t.edpro_ps.get_values()
            t.devboard.set_off()

            t.check_abs(load_values.I, volt / (LOAD_R + PS_R), 0.2, "Cannot set required current")
            t.check_abs(initial_values.U, load_values.U, 0.05, "Voltage under the load changes too much")

            reporter.trace(f"V: {volt}, actual: {initial_values.U}, load: {load_values.U}, I={load_values.I}")

        reporter.print_result()
        t.success &= reporter.success


if __name__ == "__main__":
    PSTestLoadDC().run()
