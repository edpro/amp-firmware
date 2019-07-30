import ctypes
import os


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


class Logger:

    def __init__(self, tag):
        self.tag = tag
        # enable ANSI colors in Win10 console
        if os.name == "nt":
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    def print(self, color, msg):
        print(f"{color}[{self.tag}] {msg}{Colors.RESET}")

    def trace(self, msg):
        self.print(Colors.GRAY, msg)

    def info(self, msg):
        self.print(Colors.LIGHT_BLUE, msg)

    def warn(self, msg):
        self.print(Colors.YELLOW, msg)

    def error(self, msg):
        self.print(Colors.RED, msg)


def main():
    logger = Logger("tag")
    logger.trace("trace")
    logger.info("info")
    logger.warn("warn")
    logger.error("error")


if __name__ == "__main__":
    main()
