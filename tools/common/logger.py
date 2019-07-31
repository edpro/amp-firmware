import ctypes
import os

from tools.common.screen import Colors


class LoggedError(Exception):
    pass


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
        self.print(Colors.RED, "Error: " + msg)

    def throw(self, msg):
        self.error(msg)
        raise LoggedError(msg)


def main():
    logger = Logger("tag")
    logger.trace("trace")
    logger.info("info")
    logger.warn("warn")
    logger.error("error")


if __name__ == "__main__":
    main()
