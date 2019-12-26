from tools.common.esp import flash_espinit, flash_firmware, print_esp_info, UartStr
from tools.devices.edpro_mm import EdproMM
from tools.scenarious.mm_calibration import MMCalibration, MMCalFlags
from tools.scenarious.mm_test_aac import MMTestAAC
from tools.scenarious.mm_test_adc import MMTestADC
from tools.scenarious.mm_test_r import MMTestR
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


def cal_volt_r() -> bool:
    return MMCalibration(MMCalFlags.DC0 | MMCalFlags.VDC
                         | MMCalFlags.AC0 | MMCalFlags.VAC
                         | MMCalFlags.R).run()


def test_volt_r() -> bool:
    if not MMTestVDC().run(): return False
    if not MMTestVAC(run_fast=True).run(): return False
    if not MMTestR().run(): return False
    return True


def cal_test_vr() -> bool:
    if not cal_volt_r(): return False
    if not test_volt_r(): return False
    return True


def cal_current() -> bool:
    return MMCalibration(MMCalFlags.ADC | MMCalFlags.AAC).run()


def test_current() -> bool:
    if not MMTestADC().run(): return False
    if not MMTestAAC(run_fast=True).run(): return False
    return True


def cal_test_c() -> bool:
    if not cal_current(): return False
    if not test_current(): return False
    return True


ps_menu = MenuDef([
    MenuItem("Device", submenu=MenuDef([
        MenuItem("Firmware Init", lambda: firmware_init()),
        MenuItem("Firmware Update", lambda: firmware_update()),
        MenuItem("-"),
        MenuItem("Calibrate & Test Volt/R", lambda: cal_test_vr()),
        MenuItem("Calibrate & Test Current", lambda: cal_test_c()),
        MenuItem("-"),
        MenuItem("Connect", lambda: EdproMM().show_log(), is_pause=False),
        MenuItem("Info", lambda: print_esp_info(UartStr.CP210)),

    ])),

    MenuItem("Calibration", submenu=MenuDef([
        MenuItem("AC/DC voltage & R", lambda: cal_volt_r()),
        MenuItem("AC/DC current", lambda: cal_current()),
        MenuItem("-"),
        MenuItem("DC zero", lambda: MMCalibration(MMCalFlags.DC0).run()),
        MenuItem("DC voltage", lambda: MMCalibration(MMCalFlags.VDC).run()),
        MenuItem("DC current", lambda: MMCalibration(MMCalFlags.ADC).run()),
        MenuItem("-"),
        MenuItem("AC min level", lambda: MMCalibration(MMCalFlags.AC0).run()),
        MenuItem("AC voltage", lambda: MMCalibration(MMCalFlags.VAC).run()),
        MenuItem("AC current", lambda: MMCalibration(MMCalFlags.AAC).run()),
        MenuItem("-"),
        MenuItem("Resistance", lambda: MMCalibration(MMCalFlags.R).run()),

    ])),
    MenuItem("Test", submenu=MenuDef([
        MenuItem("Test AC/DC Voltage & R", lambda: test_volt_r()),
        MenuItem("Test AC/DC Current", lambda: test_current()),
        MenuItem("-"),
        MenuItem("Test DC Voltage", lambda: MMTestVDC().run()),
        MenuItem("Test DC Current", lambda: MMTestADC().run()),
        MenuItem("-"),
        MenuItem("Test AC Voltage", lambda: MMTestVAC().run()),
        MenuItem("Test AC Current", lambda: MMTestAAC().run()),
        MenuItem("-"),
        MenuItem("Test R", lambda: MMTestR().run()),
    ])),
    MenuItem("Quit", is_quit=True),
])

ui = UI()
ui.title = "EdPro Multimeter"
ui.main_menu = ps_menu
ui.run()
