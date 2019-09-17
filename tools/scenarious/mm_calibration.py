# noinspection PyMethodParameters
from tools.scenarious.scenario import Scenario


# noinspection PyMethodParameters
class MMCalibration(Scenario):
    def __init__(self):
        super().__init__("mm_cal")

    def on_run(c):
        c.use_edpro_mm()
        c.use_meter()
        c.use_power()


if __name__ == "__main__":
    MMCalibration().run()
