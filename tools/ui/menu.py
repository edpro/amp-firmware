from typing import List, Callable, Optional

import curses

#  typings for curses in /stub are taken from:
#  https://github.com/python/typeshed/blob/master/stdlib/2and3/_curses.pyi
from tools.common.screen import init_win_console
from tools.devices.edpro_base import EdproDevice

PAIR_DEFAULT = 1
PAIR_SELECTED = 2

scr = curses.initscr()
curses.start_color()
curses.init_pair(PAIR_DEFAULT, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(PAIR_SELECTED, curses.COLOR_BLACK, curses.COLOR_WHITE)


def enable_curses():
    scr.refresh()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    scr.keypad(True)


def disable_curses():
    scr.clear()
    curses.echo()
    curses.nocbreak()
    curses.curs_set(1)
    scr.keypad(False)
    curses.endwin()


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

    def current_item(self) -> 'MenuItem':
        return self.items[self.index]


class MenuItem:
    title: str
    action: Callable
    submenu: MenuDef
    x: int = 0
    y: int = 0

    def __init__(self, title: str, action: Callable = None, submenu: MenuDef = None):
        self.title = title
        self.action = action
        self.submenu = submenu


class MenuCol:
    items: List[MenuItem]
    index: int


class UI:
    title: str = ""
    main_menu: MenuDef = None
    submenu: Optional[MenuDef] = None
    submenu_shown: bool = False

    _quit_requested: bool = False

    def draw(self):
        scr.clear()
        self.draw_title()
        self.draw_menu()
        self.draw_submenu()

    def draw_title(self):
        x = 1
        y = 1
        scr.addstr(y, x, self.title, curses.color_pair(PAIR_DEFAULT))
        y += 1
        scr.addstr(y, x, '=' * len(self.title), curses.color_pair(PAIR_DEFAULT))

    def draw_menu(self):
        x = 1
        y = 4
        scr.addstr(y, x, '|')
        x += 1
        for i, it in enumerate(self.main_menu.items):
            title = f' {self.main_menu.items[i].title} '
            color_num = PAIR_SELECTED \
                if i == self.main_menu.index and self.submenu is None \
                else PAIR_DEFAULT
            it.x = x
            it.y = y
            scr.addstr(y, x, title, curses.color_pair(color_num))
            x += len(title)
            scr.addstr(y, x, '|')
            x += 1

    def draw_submenu(self):
        if self.submenu is None:
            return
        main_item = self.main_menu.current_item()
        x = main_item.x
        y = main_item.y + 1
        scr.addstr(y, x + 1, '---')
        y += 1
        for i, it in enumerate(self.submenu.items):
            text_pair = PAIR_SELECTED if i == self.submenu.index else PAIR_DEFAULT
            it.x = x
            it.y = y
            title = f' {self.submenu.items[i].title} '
            scr.addstr(y, x, title, curses.color_pair(text_pair))
            y += 1

    def read(self) -> bool:
        ch = scr.getch()
        if ch == 27:
            if self.submenu is None:
                self.request_quit()
            else:
                self.submenu = None
                self.submenu_shown = False

        if ch == curses.KEY_LEFT:
            self.main_menu.move_prev()
            if self.submenu_shown:
                self.submenu = self.main_menu.current_item().submenu

        elif ch == curses.KEY_RIGHT:
            self.main_menu.move_next()
            if self.submenu_shown:
                self.submenu = self.main_menu.current_item().submenu

        elif ch == curses.KEY_UP:
            if self.submenu:
                self.submenu.move_prev()

        elif ch == curses.KEY_DOWN:
            if self.submenu:
                self.submenu.move_next()

        elif ch == curses.KEY_ENTER or ch == 10 or ch == 13:
            it = self.main_menu.current_item()
            if it.action:
                it.action()
            elif not self.submenu_shown:
                self.submenu_shown = True
                self.submenu = self.main_menu.current_item().submenu
            elif self.submenu:
                action = self.submenu.current_item().action
                if action:
                    disable_curses()
                    action()
                    enable_curses()

        elif ch == ord('q'):
            self._quit_requested = True

        return not self._quit_requested

    def show_menu(self):
        enable_curses()
        self.draw()
        while self.read():
            self.draw()
        disable_curses()

    def request_quit(self):
        self._quit_requested = True


def dev_run():
    init_win_console()
    ui = UI()
    ui.title = "DEVICE_NAME"
    ui.main_menu = MenuDef([
        MenuItem("Device", submenu=MenuDef([
            MenuItem("Connect", lambda: EdproDevice().show_log()),
            MenuItem("Flash Firmware"),
        ])),
        MenuItem("Calibration", submenu=MenuDef([
            MenuItem("Calibrate ALL"),
            MenuItem("Calibrate VDC"),
            MenuItem("Calibrate VAC"),
            MenuItem("Calibrate ADC"),
            MenuItem("Calibrate AAC"),
        ])),
        MenuItem("Test", submenu=MenuDef([
            MenuItem("Test ALL"),
            MenuItem("Test VDC"),
            MenuItem("Test VAC"),
            MenuItem("Test ADC"),
            MenuItem("Test AAC"),
        ])),
        MenuItem("Quit", action=lambda: ui.request_quit()),
    ])
    ui.show_menu()


if __name__ == "__main__":
    dev_run()
