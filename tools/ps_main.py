import os

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def draw_menu():
    clear()
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
    key = input("Enter your choise: ")
    if key == "q":
        return False

    if key == "f":
        print("f")
    elif key == "c":
        print("c")
    elif key == "t":
        print("t")

    return True

def main():
    while get_choise():
        pass


main()
