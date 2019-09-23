from tools.common.esp import flash_espinit, flash_firmware
from tools.devices.edpro_mm import EdproMM
from tools.scenarious.mm_calibration import MMCalibration, MMCalFlags
from tools.scenarious.mm_test_vac import MMTestVAC
from tools.scenarious.mm_test_vdc import MMTestVDC
from tools.ui.menu import MenuDef, MenuItem, UI


def firmware_init():
    flash_espinit()
    flash_firmware("./images/multimeter")


def firmware_update():
    flash_firmware("./images/multimeter")


def test_all():
    pass


ps_menu = MenuDef([
    MenuItem("Device", submenu=MenuDef([
        MenuItem("Firmware Init", lambda: firmware_init()),
        MenuItem("Firmware Update", lambda: firmware_update()),
        MenuItem("Connect", EdproMM().show_log, is_pause=False),
    ])),
    MenuItem("Calibration", submenu=MenuDef([
        MenuItem("Calibrate ALL", MMCalibration(MMCalFlags.ALL).run),
        MenuItem("--------"),
        MenuItem("Calibrate VDC", MMCalibration(MMCalFlags.VDC).run),
        MenuItem("Calibrate VAC", MMCalibration(MMCalFlags.VAC).run),
        MenuItem("--------"),
        MenuItem("Calibrate ADC", MMCalibration(MMCalFlags.ADC).run),
        MenuItem("Calibrate AAC", MMCalibration(MMCalFlags.AAC).run),
        MenuItem("--------"),
        MenuItem("Calibrate R", MMCalibration(MMCalFlags.R).run),
    ])),
    MenuItem("Test", submenu=MenuDef([
        MenuItem("Test ALL", test_all),
        MenuItem("--------"),
        MenuItem("Test VDC", MMTestVDC().run),
        MenuItem("Test VAC", MMTestVAC().run),
    ])),
    MenuItem("Quit", is_quit=True),
])

ui = UI()
ui.title = "EdPro Multimeter"
ui.main_menu = ps_menu
ui.run()
