#!/usr/bin/python3
import os
import sys
import urwid
from urwid.command_map import command_map, CURSOR_UP, CURSOR_DOWN
from gpd_ui.app import App
from gpd_ui.views import FosdemView, SyslogView, NotesView
from gpd_ui.fosdem import Fosdem

palette = [
    ('header', 'white', 'dark blue'),
    ('subheader', 'yellow', 'black'),
    ('nav', 'white', 'dark blue'),
    ('search', 'white', 'dark blue'),
]

def fosdem(app, fosdem_xml=None):
    if fosdem_xml is None:
        fosdem_xml = os.environ.get('UI_FOSDEM', '/var/lib/ui/fosdem.xml')
    fosdem = Fosdem.from_file(fosdem_xml, app.data)
    return FosdemView(app, fosdem=fosdem)

def dummy(*args, **kwargs):
    return urwid.Filler(urwid.Text('dummy'))

views = [
    ('matrix', dummy),
    ('notes', NotesView),
    ('fosdem', fosdem),
    ('system', SyslogView),
]

command_map['k'] = CURSOR_UP
command_map['j'] = CURSOR_DOWN

app = App('gpd', views, dbpath=os.environ.get('UI_DB', '/var/lib/ui/data.db'))

loop = urwid.MainLoop(
    app, palette,
    unhandled_input=app.on_unhandled_input,
)
loop.run()
