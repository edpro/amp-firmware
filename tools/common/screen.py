import ctypes
import os

win_console_initialized = False

def init_win_console():
    global win_console_initialized
    if win_console_initialized:
        return
    # enable ANSI colors in Win10 console
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    win_console_initialized = True


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    GRAY = '\033[37m'

    LIGHT_RED = '\033[91m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_MAGENTA = '\033[95m'
    LIGHT_CYAN = '\033[96m'
    LIGHT_WHITE = '\033[97m'

    RED_BG = '\033[1;41m'

    RESET = '\033[0m'


def print_color(msg: str, color: str):
    print(f'{color}{msg}{Colors.RESET}')


def prompt(msg: str):
    return input(f"\n{Colors.GREEN}>> {msg}{Colors.RESET}")
