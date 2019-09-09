from tools.common.screen import prompt, clear
from tools.common.utils import flush_firmware, flush_esp_init
from tools.devices.edpro_device import EdproMM
from tools.mm_cal import mm_run_calibration, mm_run_cal_vac, mm_run_cal_vdc


def draw_menu():
    clear()
    print("---------------------")
    print(" EdPro Multimeter")
    print("---------------------")
    print(" (i) Firmware Init")
    print(" (u) Firmware Update")
    print(" (c) Calibrate Device")
    print(" (c1) Calibrate DC Voltage")
    print(" (c2) Calibrate AC Voltage")
    # print(" (t) Test Device")
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
        flush_firmware("./images/multimeter")
        input("Press <ENTER> to continue...")

    elif key == "u":
        print("update")
        flush_firmware("./images/multimeter")
        input("Press <ENTER> to continue...")

    elif key == "c":
        print("calibration")
        mm_run_calibration()
        input("Press <ENTER> to continue...")

    elif key == "c1":
        print("calibration (VDC)")
        mm_run_cal_vdc()
        input("Press <ENTER> to continue...")

    elif key == "c2":
        print("calibration (VAC)")
        mm_run_cal_vac()
        input("Press <ENTER> to continue...")

    elif key == "t":
        print("test")

    elif key == "l":
        print("log")
        mm = EdproMM()
        mm.show_log()


def main():
    while True:
        try:
            process_menu()
        except KeyboardInterrupt:
            pass


main()
