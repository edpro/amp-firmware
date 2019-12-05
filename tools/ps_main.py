from tools.common.esp import flash_espinit, flash_firmware, print_esp_info, UartStr
from tools.devices.edpro_ps import EdproPS
from tools.scenarious.ps_calibration import PSCalibration
from tools.scenarious.ps_test_adc import PSTestADC
from tools.scenarious.ps_test_freq import PSTestFreq
from tools.scenarious.ps_test_vac import PSTestVAC
from tools.scenarious.ps_test_vdc import PSTestVDC
from tools.ui.menu import MenuDef, MenuItem, UI


def firmware_init():
    success = flash_espinit(UartStr.CP210)
    if not success:
        return
    flash_firmware("./images/powersource", UartStr.CP210)


def firmware_update():
    flash_firmware("./images/powersource", UartStr.CP210)


def test_all():
    pass


ps_menu = MenuDef([
    MenuItem("Device", submenu=MenuDef([
        MenuItem("Firmware Init", lambda: firmware_init()),
        MenuItem("Firmware Update", lambda: firmware_update()),
        MenuItem("Connect", EdproPS().show_log, is_pause=False),
        MenuItem("Info", lambda: print_esp_info(UartStr.CP210)),
    ])),
    MenuItem("Calibration", submenu=MenuDef([
        MenuItem("Calibrate ALL", lambda: PSCalibration().run()),
    ])),
    MenuItem("Test", submenu=MenuDef([
        MenuItem("Test ALL", test_all),
        MenuItem("--------"),
        MenuItem("Test VDC", PSTestVDC().run),
        MenuItem("Test VAC", PSTestVAC().run),
        MenuItem("Test ADC", PSTestADC().run),
        MenuItem("Test AAC", PSTestVAC().run),
        MenuItem("--------"),
        MenuItem("Test FREQ", PSTestFreq().run),
    ])),
    MenuItem("Quit", is_quit=True),
])

ui = UI()
ui.title = "EdPro PowerSource"
ui.main_menu = ps_menu
ui.run()
