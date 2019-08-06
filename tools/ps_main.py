from tools.common.logger import LoggedError
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
    print("(t) Test Device")
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

    if key == "1":
        print("init")
        flush_esp_init()
        flush_firmware("./images/powersource")
        input("Press <ENTER> to continue...")
        return True

    if key == "2":
        print("update")
        flush_firmware("./images/powersource")
        input("Press <ENTER> to continue...")
        return True

    if key == "f":
        print("flush")
        return True

    if key == "c":
        print("calibration")
        ps_run_calibration()
        input("Press <ENTER> to continue...")
        return True

    elif key == "t":
        print("test")
        return True

    elif key == "l":
        print("log")
        ps = EdproPS()
        try:
            ps.connect()
            ps.wait_boot_complete()
            ps.cmd("devmode")
            prompt("Press <Enter> to close...\n")
        except LoggedError:
            pass
        except KeyboardInterrupt:
            pass
        except Exception:
            raise
        finally:
            ps.close()
        return True


def main():
    while process_menu():
        pass


main()
