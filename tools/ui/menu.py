import curses

#  typings for curses in /stub are taken from:
#  https://github.com/python/typeshed/blob/master/stdlib/2and3/_curses.pyi
from tools.common.screen import init_win_console

scr = curses.initscr()
curses.start_color()


def init_curses():
    curses.noecho()
    curses.cbreak()
    scr.keypad(True)


def dispose_curses():
    curses.nocbreak()
    scr.keypad(False)
    curses.echo()
    curses.endwin()


class Menu():
    def __init__(self):
        pass

    def show(self):
        init_curses()
        scr.clear()
        scr.addstr(0, 0, 'curses.A_REVERSE', curses.A_REVERSE)
        scr.addstr(1, 0, 'curses.A_BOLD', curses.A_BOLD)
        scr.addstr(2, 0, 'curses.A_STANDOUT', curses.A_STANDOUT)
        scr.addstr(3, 0, 'curses.A_DIM', curses.A_DIM)
        scr.addstr(4, 0, 'DEFAULT')
        scr.addstr(5, 0, "Pretty text", curses.color_pair(1))
        scr.addstr(6, 0, "Pretty text", curses.color_pair(2))

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        scr.addstr(7, 0, f"has_color: {curses.has_colors()}", curses.color_pair(1))
        scr.addstr(7, 0, f"can_change_color: {curses.can_change_color()}")
        scr.refresh()

    def hide(self):
        scr.clear()
        dispose_curses()


def dev_run():
    init_win_console()
    m = Menu()
    m.show()
    scr.getkey()
    m.hide()


if __name__ == "__main__":
    dev_run()
