import curses

#  typings for curses in /stub are taken from:
#  https://github.com/python/typeshed/blob/master/stdlib/2and3/_curses.pyi

scr = curses.initscr()


def init_curses():
    curses.noecho()
    curses.cbreak()
    scr.keypad(True)


def dispose_curses():
    curses.nocbreak()
    scr.keypad(False)
    curses.echo()


class Menu():
    def __init__(self):
        pass

    def show(self):
        init_curses()
        scr.clear()
        for i in range(0, 11):
            scr.addstr(i, 0, '10 divided by')
        scr.refresh()

    def hide(self):
        scr.clear()
        dispose_curses()


def dev_run():
    m = Menu()
    m.show()
    scr.getkey()
    m.hide()


if __name__ == "__main__":
    dev_run()
