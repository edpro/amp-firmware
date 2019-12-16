from tools.common.esp import flash_espinit, flash_firmware, print_esp_info, UartStr
from tools.devices.edpro_mm import EdproMM
from tools.scenarious.mm_calibration import MMCalibration, MMCalFlags
from tools.scenarious.mm_test_vac import MMTestVAC
from tools.scenarious.mm_test_vdc import MMTestVDC
from tools.ui.menu import MenuDef, MenuItem, UI


def firmware_init():
    success = flash_espinit(UartStr.CP210)
    if not success:
        return
    flash_firmware("./images/multimeter", UartStr.CP210)


def firmware_update():
    flash_firmware("./images/multimeter", UartStr.CP210)


def test_all():
    pass


ps_menu = MenuDef([
    MenuItem("Device", submenu=MenuDef([
        MenuItem("Firmware Init", lambda: firmware_init()),
        MenuItem("Firmware Update", lambda: firmware_update()),
        MenuItem("Connect", lambda: EdproMM().show_log(), is_pause=False),
        MenuItem("Info", lambda: print_esp_info(UartStr.CP210)),

    ])),
    MenuItem("Calibration", submenu=MenuDef([
        MenuItem("Calibrate ALL", lambda: MMCalibration(MMCalFlags.ALL).run()),
        MenuItem("--------"),
        MenuItem("Calibrate DC0", lambda: MMCalibration(MMCalFlags.DC0).run()),
        MenuItem("Calibrate VDC", lambda: MMCalibration(MMCalFlags.VDC).run()),
        MenuItem("Calibrate ADC", lambda: MMCalibration(MMCalFlags.ADC).run()),
        MenuItem("--------"),
        MenuItem("Calibrate AC0", lambda: MMCalibration(MMCalFlags.AC0).run()),
        MenuItem("Calibrate VAC", lambda: MMCalibration(MMCalFlags.VAC).run()),
        MenuItem("Calibrate AAC", lambda: MMCalibration(MMCalFlags.AAC).run()),
        MenuItem("--------"),
        MenuItem("Calibrate R", lambda: MMCalibration(MMCalFlags.R).run()),

    ])),
    MenuItem("Test", submenu=MenuDef([
        MenuItem("Test ALL", test_all),
        MenuItem("--------"),
        MenuItem("Test VDC", lambda: MMTestVDC().run()),
        MenuItem("Test VAC", lambda: MMTestVAC().run()),
    ])),
    MenuItem("Quit", is_quit=True),
])

ui = UI()
ui.title = "EdPro Multimeter"
ui.main_menu = ps_menu
ui.run()
