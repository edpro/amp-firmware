def draw_menu():
    print("\n")
    print("Select:")
    print("---------------------")
    print("(f) Flush firmware")
    print("(c) Calibrate")
    print("(t) Test")


def make_choise():
    nb = input('Choose a number: ')
    print(nb)


def main():
    draw_menu()
    make_choise()

main()