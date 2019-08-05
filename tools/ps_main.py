import os
import sys

sys.path.insert(0, ".")

from tools.common.logger import LoggedError
from tools.ps_cal import ps_calibration


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def draw_menu():
    # clear()
    print("---------------------")
    print("EdPro Powersource")
    print("---------------------")
    print("(f) Flush firmware")
    print("(c) Calibrate")
    print("(t) Test")
    print("(q) Quit")
    print()


def get_choise() -> bool:
    draw_menu()

    try:
        key = input("Enter your choise: ")
    except KeyboardInterrupt:
        key="q"
    except Exception:
        raise

    if key == "q":
        print("quit")
        return False

    if key == "f":
        print("flush")
    elif key == "c":
        print("calibration")
        try:
            # ps_calibration()
            input("Press <ENTER> to continue...")
        except LoggedError:
            pass
        except Exception:
            raise
    elif key == "t":
        print("test")

    return True


def main():
    while get_choise():
        pass


main()
