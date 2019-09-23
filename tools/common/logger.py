from tools.common.screen import Colors, scr_init


class LoggedError(Exception):
    pass


class Logger:

    def __init__(self, tag):
        self.tag = tag
        scr_init()

    def print(self, color, msg):
        print(f"{color}[{self.tag}] {msg}{Colors.RESET}")

    def trace(self, msg):
        self.print(Colors.GRAY, msg)

    def success(self, msg="OK"):
        self.print(Colors.GREEN, msg)

    def info(self, msg):
        self.print(Colors.LIGHT_BLUE, msg)

    def warn(self, msg):
        self.print(Colors.YELLOW, msg)

    def error(self, msg):
        self.print(Colors.LIGHT_RED, "Error: " + str(msg))

    def throw(self, msg):
        self.error(str(msg))
        raise LoggedError(msg)


def main():
    logger = Logger("tag")
    logger.trace("trace")
    logger.info("info")
    logger.warn("warn")
    logger.error("error")


if __name__ == "__main__":
    main()
