#!/usr/bin/python3
import os
import sys
import urwid
from urwid.command_map import command_map, CURSOR_UP, CURSOR_DOWN
from enpda.app import App
from enpda.views import FosdemView, SyslogView, NotesView
from enpda.fosdem import Fosdem

palette = [
    ('header', 'white', 'dark blue'),
    ('subheader', 'yellow', 'black'),
    ('nav', 'white', 'dark blue'),
    ('search', 'white', 'dark blue'),
    ('success', 'black,bold', 'dark green'),
    ('active', 'default,bold,underline', 'default'),
]

def fosdem(app, fosdem_xml=None):
    if fosdem_xml is None:
        fosdem_xml = os.environ.get('ENPDA_FOSDEM', '/var/lib/enpda/fosdem.xml')
    fosdem = Fosdem.from_file(fosdem_xml, app.data)
    return FosdemView(app, fosdem=fosdem)

views = [
    ('notes', NotesView),
    ('fosdem', fosdem),
    ('system', SyslogView),
]

command_map['k'] = CURSOR_UP
command_map['j'] = CURSOR_DOWN

app = App('enpda', views, dbpath=os.environ.get('ENPDA_DB', '/var/lib/enpda/data.db'))


loop = urwid.MainLoop(
    app, palette,
    unhandled_input=app.on_unhandled_input,
)
loop.run()
