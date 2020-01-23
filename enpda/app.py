import urwid
from enpda.data import Data
from enpda.widgets import Header, NavMenu

class App(urwid.Frame):
    def __init__(self, name, views, dbpath='/var/lib/ui/data.db', title=None):
        self.name = name
        self.data = Data(dbpath)
        self.view_list = [x[0] for x in views]
        self.views = {x[0]: x[1] for x in views}
        self.current_view = self.view_list[0]
        self.title = title or self.current_view
        self._title = Header(self.name, self.title)

        super().__init__(
            header=urwid.AttrMap(self._title, 'header'),
            body=self.views[self.current_view](self),
            footer=urwid.AttrMap(NavMenu(self, self.view_list), 'nav'),
            focus_part='footer',
        )

    def terminate(self):
        raise urwid.ExitMainLoop()

    def keypress(self, size, key):
        handled = self.focus.keypress(size, key) is None
        if handled:
            return

        cmdmap = {
            'q': lambda: self.terminate(),
            'esc': lambda: self.set_focus('footer'),
        }

        try:
            cmdmap[key]()
        except KeyError:
            return key

    def change_view(self, name, *viewparams):
        self._title.update_title(name)
        self.current_view = name
        contents = self.contents
        contents['body'] = (self.views[name](self, *viewparams), self.options())
        self._invalidate()

    def on_unhandled_input(self, key):
        if key == 'q':
            raise urwid.ExitMainLoop()
