import urwid
from urwid.command_map import CURSOR_UP, CURSOR_DOWN

class SelectableText(urwid.SelectableIcon):
    def __init__(self, *args, cursor_position=0, **kwargs):
        super().__init__(*args, **kwargs, cursor_position=cursor_position)

class NavItem(SelectableText):
    def __init__(self, menu, name):
        self.menu = menu
        self.name = name
        super().__init__(('nav', name))

class NavMenu(urwid.Columns):
    def __init__(self, app, items):
        self.app = app
        super().__init__(
            [NavItem(self, x) for x in items] +
            [urwid.Text("00:00", "right")]
        )

    def keypress(self, size, key):
        if key == 'enter':
            self.app.change_view(self.focus.name)
            return
        if key in ['up', 'k']:
            if self.app.contents['body'][0].selectable():
                self.app.set_focus('body')
            return
        if key == 'h':
            key = 'left'
        if key == 'l':
            key = 'right'
        return super().keypress(size, key)

class Header(urwid.Text):
    def __init__(self, appname, title):
        self.appname = appname
        super().__init__('%s: %s' % (appname, title), 'center')

    def update_title(self, title):
        self.set_text('%s: %s' % (self.appname, title))
