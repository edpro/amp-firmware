from tools.common.screen import prompt, clear
from tools.common.utils import flush_firmware, flush_esp_init
from tools.devices.edpro_ps import EdproPS


def draw_menu():
    clear()
    print("---------------------")
    print(" EdPro Powersource")
    print("---------------------")
    print(" (i) Firmware Init")
    print(" (u) Firmware Update")
    print(" (c) Calibrate Device")
    print(" (t) Test Device")
    print(" (l) Log")
    print(" (q) Quit")


def process_menu():
    draw_menu()

    try:
        key = prompt("Enter your choise: ")
    except KeyboardInterrupt:
        key = "q"

    if key == "q":
        print("quit")
        exit(0)

    elif key == "i":
        print("init")
        flush_esp_init()
        flush_firmware("./images/powersource")
        input("Press <ENTER> to continue...")

    elif key == "u":
        print("update")
        flush_firmware("./images/powersource")
        input("Press <ENTER> to continue...")

    elif key == "c":
        print("calibration")
        # ps_run_calibration()
        input("Press <ENTER> to continue...")

    elif key == "t":
        # ps_run_test()
        print("test")
        input("Press <ENTER> to continue...")

    elif key == "l":
        print("log")
        EdproPS().show_log()


def main():
    while True:
        try:
            process_menu()
        except KeyboardInterrupt:
            pass


main()
