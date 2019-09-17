from tools.common.esp import flash_espinit, flash_firmware
from tools.common.screen import prompt, clear
from tools.devices.edpro_mm import EdproMM
from tools.mm_cal import mm_run_calibration, mm_run_cal_vac, mm_run_cal_vdc
from tools.scenarious.mm_test_vac import MMTestVAC
from tools.scenarious.mm_test_vdc import MMTestVDC


def draw_menu():
    clear()
    print("---------------------")
    print(" EdPro Multimeter")
    print("---------------------")
    print(" [i] - Firmware Init")
    print(" [u] - Firmware Update")
    print(" [l] - Device Log")
    print("---------------------")
    print(" [c]  - Calibrate Device")
    print(" [c1] - Calibrate DC Voltage")
    print(" [c2] - Calibrate AC Voltage")
    print("---------------------")
    print(" [tvdc] - Test DC Voltage")
    print(" [tvac] - Test AC Voltage")
    print("---------------------")
    print(" [q] - Quit")


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
        flash_espinit()
        flash_firmware("./images/multimeter")
        input("Press <ENTER> to continue...")

    elif key == "u":
        print("update")
        flash_firmware("./images/multimeter")
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

    elif key == "tvdc":
        print("test VDC")
        MMTestVDC().run()
        input("Press <ENTER> to continue...")

    elif key == "tvac":
        print("test VAC")
        MMTestVAC().run()
        input("Press <ENTER> to continue...")

    elif key == "l":
        print("log")
        EdproMM().show_log()


def main():
    while True:
        try:
            process_menu()
        except KeyboardInterrupt:
            pass


main()
