import urwid
import logging
from collections import defaultdict
from enpda.view import View
from enpda.widgets import SelectableText

class NoteDB:
    def __init__(self, db, hooks=None):
        self.db = db
        self.hooks = hooks or defaultdict(lambda: lambda note: None)

    @property
    def list(self):
        return [n[1] for n in self.db.get_collection('note')]

    def get_value(self, title):
        return self.db.get_value('note', title)

    def get_note(self, title):
        return Note(self, title, self.get_value(title))

    def create(self, title, content):
        self.db.insert('note', title, content)
        self.hooks['on_create'](title)

    def update(self, title, content):
        self.db.update('note', title, content)
        self.hooks['on_update'](title)

class Note:
    def __init__(self, db, title, content=None):
        self.title = title
        self.db = db
        self.new = self.is_new()
        self._content = content

    def get_content(self):
        return self.db.get_value(self.title)

    def is_new(self):
        return self.get_content() is None

    @property
    def content(self):
        if not self.new and self._content is None:
            self._content = self.get_content()
        return self._content

    @content.setter
    def content(self, value):
        self.save(value)

    def create(self, content):
        self.db.create(self.title, content)
        self.new = False

    def save(self, content):
        content = content or ''
        if self.new:
            self.create(content)
        else:
            self.db.update(self.title, content)
        self._content = content

    def flush_cache(self):
        self._content = None

    def __str__(self):
        return str((self.title, self.content))


class NotesView(View):
    def __init__(self, app, init_state=(), *args, **kwargs):
        self.app = app
        self.notes = NotesColumns(
            NoteDB(app.data, hooks={
                'on_create': self.update_list
            }),
            init_state
        )
        super().__init__(app, *args, body=self.notes, **kwargs)

    def update_list(self, title):
        self.notes.update_list(title)

class NotesColumns(urwid.Columns):
    def __init__(self, notes, init_state=()):
        self.notes = notes

        self.note_list = NotesList(self, self.notes)
        initial_widgets = [self.note_list]

        super().__init__(initial_widgets)

        if 'open' in init_state:
            self.show_left(Editor(notes.get_note(init_state['open'])))

    def update_list(self, title):
        self.contents[0] = (NotesList(self, self.notes), self.options())

    def show_left(self, widget):
        l = len(self.contents)
        if l == 1:
            self.contents.append((widget, self.options()))
        elif l:
            self.contents[1] = (widget, self.options())
        self.set_focus(widget)

    def keypress(self, size, key):
        if key == 'tab':
            self.focus_position ^= 1
            return
        return super().keypress(size, key)

class NotenamePrompt(urwid.Filler):
    def __init__(self, on_submit):
        super().__init__(NotenamePromptEdit(on_submit))

class NotenamePromptEdit(urwid.Edit):
    def __init__(self, on_submit):
        self.on_submit = on_submit
        super().__init__(caption='Name: ')

    def keypress(self, size, key):
        if key == 'enter':
            self.on_submit(self.edit_text)
            return
        return super().keypress(size, key)

class NotesList(urwid.ListBox):
    def __init__(self, parent, notes):
        self.parent = parent
        self.notes = notes
        super().__init__(
            [SelectableText(n) for n in notes.list]
        )

    def open_note(self, title):
        self.parent.show_left(Editor(Note(self.notes, title)))

    def new_note(self, title):
        self.open_note(title)

    def keypress(self, size, key):
        if key == 'enter':
            self.open_note(self.focus.get_text()[0])
            return
        if key == 'n':
            self.parent.show_left(NotenamePrompt(self.new_note))
            return
        return super().keypress(size, key)

class EditorPrompt(urwid.Edit):
    def __init__(self):
        super().__init__(caption='')

class Buffer(urwid.Filler):
    def __init__(self, content):
        super().__init__(BufferEdit(content), 'top')

    @property
    def edit_text(self):
        return self.body.edit_text

class BufferEdit(urwid.Edit):
    def __init__(self, content):
        super().__init__(edit_text=content or '', multiline=True)

class Editor(urwid.Frame):
    def __init__(self, note):
        self.note = note
        self._mode = 'normal'
        self.keypress_map = {
            'cmd': self.keypress_cmd,
            'normal': self.keypress_normal,
            'insert': self.keypress_insert,
        }
        self.prompt = EditorPrompt()
        self.buffer = Buffer(note.content)

        super().__init__(
            header=urwid.AttrMap(urwid.Text(note.title), 'header'),
            body=self.buffer,
            footer=self.prompt,
        )

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        if mode == self.mode:
            return
        if mode == 'cmd':
            self.prompt.set_caption(':')
            self.focus_position = 'footer'
        if mode == 'normal':
            self.prompt.set_caption('')
            self.focus_position = 'body'
        if mode == 'insert':
            self.prompt.set_caption('(ins)')
            self.focus_position = 'body'
        self._mode = mode

    def keypress_movement(self, size, key):
        # TODO: $, b, w, G, gg
        coords = self.buffer.get_cursor_coords(size)
        if key == 'h':
            coords = (coords[0]-1, coords[1])
        if key == 'k':
            coords = (coords[0], coords[1]-1)
        if key == 'j':
            coords = (coords[0], coords[1]+1)
        if key == 'l':
            coords = (coords[0]+1, coords[1])
        if key == 'g':
            coords = (coords[0], 0)
        if key == '^':
            coords = (0, coords[1])
        if key == '$':
            coords = (0, coords[1])
        self.buffer.move_cursor_to_coords(size, *coords)

    def keypress_normal(self, size, key):
        if key == 'i':
            self.mode = 'insert'
        elif key == ':':
            self.mode = 'cmd'
        elif key in ['^', 'g', 'G', 'b', 'w', 'h', 'j', 'k', 'l', '$']:
            return self.keypress_movement(size, key)
        else:
            return key

    def cmd_set(self, *args):
        pass

    def cmd_w(self, *args):
        self.note.save(self.buffer.edit_text)

    def cmd_execute(self, cmd, *args):
        try:
            {
                'w': self.cmd_w,
                'set': self.cmd_set,
            }[cmd](*args)
        except KeyError:
            pass

    def keypress_cmd(self, size, key):
        if key == 'enter':
            text = self.prompt.edit_text
            if text:
                self.cmd_execute(*text.split())

        if key in ['esc', 'enter']:
            self.prompt.edit_text = ''
            self.mode = 'normal'
        else:
            return super().keypress(size, key)

    def keypress_insert(self, size, key):
        if key == 'esc':
            self.mode = 'normal'
        else:
            return super().keypress(size, key)

    def keypress(self, size, key):
        if self.mode == 'normal':
            return self.keypress_normal(size, key)
        elif self.mode == 'cmd':
            return self.keypress_cmd(size, key)
        elif self.mode == 'insert':
            return self.keypress_insert(size, key)
        else:
            return key
