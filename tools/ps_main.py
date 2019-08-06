from tools.common.screen import prompt, clear
from tools.common.utils import flush_firmware, flush_esp_init
from tools.edpro_device import EdproPS
from tools.ps_cal import ps_run_calibration


def draw_menu():
    clear()
    print("---------------------")
    print("EdPro Powersource")
    print("---------------------")
    print("(1) Firmware Init")
    print("(2) Firmware Update")
    print("(c) Calibrate Device")
    # print("(t) Test Device")
    print("(l) Log")
    print("(q) Quit")


def process_menu() -> bool:
    draw_menu()

    try:
        key = prompt("Enter your choise: ")
    except KeyboardInterrupt:
        key = "q"
    except Exception:
        raise

    if key == "q":
        return False

    elif key == "1":
        print("init")
        flush_esp_init()
        flush_firmware("./images/powersource")
        input("Press <ENTER> to continue...")
        return True

    elif key == "2":
        print("update")
        flush_firmware("./images/powersource")
        input("Press <ENTER> to continue...")

    elif key == "f":
        print("flush")

    elif key == "c":
        print("calibration")
        ps_run_calibration()
        input("Press <ENTER> to continue...")

    elif key == "t":
        print("test")

    elif key == "l":
        print("log")
        ps = EdproPS()
        ps.show_log()

    return True


def main():
    while process_menu():
        pass


main()
