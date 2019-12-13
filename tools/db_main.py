from tools.common.esp import flash_firmware, print_esp_info, UartStr
from tools.devices.edpro_db import EdproDevBoard
from tools.scenarious.db_test import db_run_test
from tools.ui.menu import MenuDef, MenuItem, UI


def firmware_update():
    flash_firmware("./images/devboard", UartStr.CP210)


ps_menu = MenuDef([
    MenuItem("Device", submenu=MenuDef([
        MenuItem("Firmware Update", lambda: firmware_update()),
        MenuItem("Console", EdproDevBoard().show_log, is_pause=False),
        MenuItem("Info", lambda: print_esp_info(UartStr.CP210)),
    ])),
    MenuItem("Test", submenu=MenuDef([
        MenuItem("Run test", db_run_test),
    ])),
    MenuItem("Quit", is_quit=True),
])

ui = UI()
ui.title = "Development Board"
ui.main_menu = ps_menu
ui.run()
