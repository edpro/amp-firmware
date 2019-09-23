from typing import List, Callable

import curses

#  typings for curses in /stub are taken from:
#  https://github.com/python/typeshed/blob/master/stdlib/2and3/_curses.pyi
from tools.common.screen import init_win_console

PAIR_DEFAULT = 1
PAIR_SELECTED = 2

scr = curses.initscr()
curses.start_color()
curses.init_pair(PAIR_DEFAULT, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(PAIR_SELECTED, curses.COLOR_BLACK, curses.COLOR_WHITE)


class MenuDef:
    items: List['MenuItem'] = []
    index: int = 0

    def __init__(self, items: List['MenuItem']):
        self.items = items
        self.index = 0

    def move_prev(self):
        self.index = (self.index - 1) % len(self.items)

    def move_next(self):
        self.index = (self.index + 1) % len(self.items)


class MenuItem:
    title: str
    action: Callable
    submenu: MenuDef

    def __init__(self, title: str, action: Callable = None, submenu: MenuDef = None):
        self.title = title
        self.action = action
        self.submenu = submenu


class MenuCol:
    items: List[MenuItem]
    index: int


class UI:
    title: str
    main_menu: MenuDef

    def init(self):
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        scr.keypad(True)

    def dispose(self):
        curses.nocbreak()
        curses.curs_set(1)
        scr.keypad(False)
        curses.echo()
        curses.endwin()

    def draw_title(self):
        x = 1
        y = 1
        scr.addstr(y, x, self.title, curses.color_pair(PAIR_DEFAULT))

    def draw_menu(self):
        x = 1
        y = 3
        scr.addstr(y, x, '|')
        x += 1
        for i, it in enumerate(self.main_menu.items):
            if i == self.main_menu.index:
                text_pair = PAIR_SELECTED
            else:
                text_pair = PAIR_DEFAULT
            title = f' {self.main_menu.items[i].title} '
            scr.addstr(y, x, title, curses.color_pair(text_pair))
            x += len(title)
            scr.addstr(y, x, '|')
            x += 1

    def draw(self):
        scr.clear()
        self.draw_title()
        self.draw_menu()
        scr.refresh()

    def read(self) -> bool:
        ch = scr.getkey()
        if ch == 'KEY_LEFT':
            self.main_menu.move_prev()
        elif ch == 'KEY_RIGHT':
            self.main_menu.move_next()
        elif ch == 'q':
            return False
        return True

    def show_menu(self):
        self.draw()
        while self.read():
            self.draw()


def dev_run():
    init_win_console()
    ui = UI()
    ui.init()
    ui.title = "DEVICE_NAME:"
    ui.main_menu = MenuDef([
        MenuItem("Flash"),
        MenuItem("Test"),
        MenuItem("Calibration"),
        MenuItem("Quit"),
    ])
    ui.show_menu()
    ui.dispose()


if __name__ == "__main__":
    dev_run()
