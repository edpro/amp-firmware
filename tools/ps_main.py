from tools.common.logger import LoggedError
from tools.common.screen import prompt, clear
from tools.edpro_device import EdproPS
from tools.ps_cal import ps_run_calibration


def draw_menu():
    print()
    print("---------------------")
    print("EdPro Powersource")
    print("---------------------")
    print("(f) Flush firmware")
    print("(c) Calibrate")
    print("(t) Test")
    print("(l) Log")
    print("(q) Quit")


def get_choise() -> bool:
    draw_menu()

    try:
        key = prompt("Enter your choise: ")
    except KeyboardInterrupt:
        key = "q"
    except Exception:
        raise

    if key == "q":
        print("quit")
        return False

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
    while get_choise():
        pass


main()
