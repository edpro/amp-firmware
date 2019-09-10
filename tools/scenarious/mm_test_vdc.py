from tools.common.tests import eabs, erel, TestReporter
from tools.devices.rigol_meter import RigolMode
from tools.scenarious.scenario import Scenario


# noinspection PyMethodParameters
class MMTestVDC(Scenario):
    def __init__(self):
        super().__init__("test_vdc")

    def on_run(t):
        t.init_edpro_mm()
        t.init_meter()
        t.init_power()
        t.test_vdc()

    def test_vdc(t):
        t.edpro_mm.cmd("mode dc")
        mm_mode = t.edpro_mm.request_mode()
        t.check_str(mm_mode, "VDC", "Invalid device mode!")

        meter_mode = RigolMode.VDC_200m
        t.meter.set_mode(meter_mode)
        t.power.set_volt(0)
        t.wait(1)

        r = TestReporter(t.tag)

        for v in [0.001, 0.010, 0.100, 1.0, 1.1, 10.0, 20.0, 30.0]:
            if v <= 0.1:
                if meter_mode != RigolMode.VDC_200m:
                    meter_mode = RigolMode.VDC_200m
                    t.meter.set_mode(meter_mode)
            elif v <= 1.0:
                if meter_mode != RigolMode.VDC_2:
                    meter_mode = RigolMode.VDC_2
                    t.meter.set_mode(meter_mode)
            elif v <= 10.0:
                if meter_mode != RigolMode.VDC_20:
                    meter_mode = RigolMode.VDC_20
                    t.meter.set_mode(meter_mode)
            else:
                meter_mode = RigolMode.VDC_200
                t.meter.set_mode(meter_mode)

            t.power.set_volt(v)
            t.wait(1)

            t.meter.measure_vdc()  # duty cycle
            expect = t.meter.measure_vdc()
            actual = t.edpro_mm.request_value()
            t.check(abs(v - expect) < 0.1, f"Cannot set voltage: v={v}")
            ea = eabs(expect, actual)
            er = erel(expect, actual)
            r.trace(
                f"v: {v}V | expected: {expect:0.6f} | actual: {actual:0.6f} | abs: {ea:0.6f} | rel: {er * 100:0.2f}%")
            r.expect_abs_rel(expect, actual, 0.01, 0.02)

        t.power.set_volt(0)
        r.print_result()
        t.success &= r.success


if __name__ == "__main__":
    MMTestVDC().run()
