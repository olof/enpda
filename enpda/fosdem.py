#!/usr/bin/python
import sys
from io import StringIO
from lxml import etree
import urwid
import sqlite3
from enpda.view import View
from enpda.widgets import SelectableText
from bs4 import BeautifulSoup

class FosdemAuthor:
    def __init__(self, name, fosdem_id):
        self.fosdem_id = fosdem_id
        self.name = name

    def __str__(self):
        return self.name

class FosdemAuthors:
    def __init__(self, authors):
        self.authors = authors

    def __str__(self):
        return ', '.join(map(str, self.authors))

class FosdemEvent:
    def __init__(self, title, authors, track, room, date, duration, start_time,
                 description, abstract, fosdem_id):
        self.title = title
        self.authors = authors
        self.track = track
        self.room = room
        self.date = date
        self.duration = duration
        self.start_time = start_time
        self._description = description
        self._abstract = abstract
        self.fosdem_id = fosdem_id

    @property
    def description(self):
        d = None
        if self._description:
            d = self._description
        elif self._abstract:
            d = self._abstract
        if not d:
            return 'no description given'
        return BeautifulSoup(d, 'lxml').get_text()

    def __str__(self):
        return '%s - %s\n        by %s (duration: %s)' % (
            self.start_time, self.title, self.authors, self.duration
        )

class Fosdem:
    @staticmethod
    def from_file(filename, *args, **kwargs):
        with open(filename) as fh:
            return Fosdem(fh, *args, **kwargs)

    def __init__(self, fh, db):
        self._by_tracks = {'Favorites': []}
        self._by_id = {}
        self.tracks = []
        self.trackinfo = {}
        self.db = db

        def authors(ev):
            authors = []
            for p in ev.xpath('./persons/person'):
                authors.append(FosdemAuthor(p.text, p.get('id')))
            return FosdemAuthors(authors)

        def attr(ev, key):
            return ev.xpath('./%s' % key)[0].text

        tree = etree.parse(fh)
        days = tree.xpath('/schedule/day')
        for day in days:
            dayidx = int(day.get('index'))
            date = day.get('date')
            events = day.xpath('./room/event')

            for ev in events:
                track = 'Day %d: %s' % (dayidx, attr(ev, 'track'))
                room = attr(ev, 'room')

                if not track in self.tracks:
                    self.tracks.append(track)
                    self.trackinfo[track] = {
                        'day': day,
                        'date': date,
                        'room': room,
                    }

                self._by_tracks.setdefault(track, [])
                fosdemev = FosdemEvent(
                    fosdem_id=ev.get('id'),
                    title=attr(ev, 'title'),
                    authors=authors(ev),
                    track=track,
                    room=room,
                    date=date,
                    duration=attr(ev, 'duration'),
                    start_time=attr(ev, 'start'),
                    description=attr(ev, 'description'),
                    abstract=attr(ev, 'abstract'),
                )
                self._by_tracks[track].append(fosdemev)
                self._by_id[fosdemev.fosdem_id] = fosdemev

    @property
    def favorites(self):
        return [
            self.get_event(ev[2])
            for ev in self.db.get_collection('fosdem2020_favorite')
        ]

    def get_track(self, track):
        if track == 'Favorites':
            return self.favorites, {'date': '?', 'day': '?', 'room': 'ulb'}
        return self._by_tracks[track], self.trackinfo[track]

    def get_event(self, fosdem_id):
        return self._by_id[fosdem_id]


class FosdemList(urwid.ListBox):
    def __init__(self, view, items):
        self.view = view
        self.list = items
        self.w = urwid.SimpleFocusListWalker([])
        self.filter()
        super().__init__(self.w)

    def filter(self, cb=None):
        if cb is None:
            cb = lambda _: True
        self.w.clear()
        for item in [i for i in self.list if cb(i) or i == 'Favorites']:
            self.w.append(SelectableText(item))

    def keypress(self, size, key):
        if self.focus_position == 0 and key in ['k', 'up']:
            self.view.tracklist.toggle_focus()
            return
        if key == 'enter':
            track = self.focus.text
            self.view.update_track(track, self.view.fosdem.trackinfo.get(track, {}))
            return
        return super().keypress(size, key)

class FosdemTrackListControl(urwid.Columns):
    def __init__(self, tracklist):
        self.tracklist = tracklist

        super().__init__([
            SelectableText(('active', 'All days')),
            SelectableText('Day 1'),
            SelectableText('Day 2'),
        ])

    def keypress(self, size, key):
        if key == 'enter':
            if self.focus.text.startswith('Day '):
                self.tracklist.filter(lambda line: line.startswith(self.focus.text))
            else:
                self.tracklist.filter()
            return
        if key == 'j' or key == 'down':
            self.tracklist.focus_position = 'body'
            return
        return super().keypress(size, key)

class FosdemTrackList(urwid.Frame):
    def __init__(self, view, fosdem):
        self.fosdem = fosdem
        self.list = FosdemList(view, ['Favorites'] + fosdem.tracks)
        self.ctrl = FosdemTrackListControl(self)
        #self.prompt = urwid.Edit('filter: ')
        super().__init__(
            body=self.list,
            header=self.ctrl,
            #footer=urwid.AttrMap(self.prompt, 'search'),
            focus_part='body',
        )

    def toggle_focus(self):
        if self.focus_position == 'body':
            self.focus_position = 'header'
        else:
            self.focus_position = 'body'

    def filter(self, cb=None):
        self.list.filter(cb)

    def keypress(self, size, key):
        if key == 'tab':
            self.toggle_focus()
            return
        key = self.focus.keypress(size, key)
        if not key:
            return
        return super().keypress(size, key)

class FosdemEventText(SelectableText):
    def __init__(self, ev):
        self.ev = ev
        super().__init__(str(ev))

    @property
    def fosdem_id(self):
        return self.ev.fosdem_id

class FosdemEventList(urwid.Frame):
    def __init__(self, view, *args, track=None, **kwargs):
        self.view = view
        self.list = FosdemList(view, *args, **kwargs)
        self.header = urwid.Text(
            ('subheader', ('Track: %s' % track if track else 'no track selected')),
            'center'
        )
        super().__init__(
            header=self.header,
            body=self.list,
            focus_part='body',
        )

    def change_track(self, track, events, info):
        track_title = 'Track: %s (%s) in room %s' % (
            track, info['date'], info['room']
        )

        if events:
            self.header.set_text(('subheader', '%s' % track_title))
        else:
            self.header.set_text(('subheader', '%s (no events listed)' % track_title))

        self.list.w.clear()
        self.list.w.extend([FosdemEventText(ev) for ev in events])

    def keypress(self, size, key):
        target = self.list.focus
        if target.keypress(size, key) is None:
            return
        if key == 'f':
            self.view.add_favorite(target.ev)
            return
        if key == 'd':
            self.view.remove_favorite(target.ev)
            return
        if key == 'N':
            self.view.open_note(target.ev)
            return
        if key == 'enter':
            self.list.view.show_event_details(target.ev)
            return
        return super().keypress(size, key)

    @property
    def walker(self):
        return self.list.walker

class FosdemView(View):
    def __init__(self, app, fosdem, **kwargs):
        self.fosdem_view = FosdemViewWidget(app, fosdem)
        super().__init__(app, body=self.fosdem_view)

    def keypress(self, size, key):
        if self.fosdem_view.keypress(size, key) is None:
            return
        return super().keypress(size, key)

class FosdemViewWidget(urwid.WidgetPlaceholder):
    def __init__(self, app, fosdem):
        self.app = app
        self.popup_open = False
        self.fosdem = fosdem
        super().__init__(FosdemPanes(self, fosdem))

    def add_favorite(self, event):
        sortkey = '%s_%s_%s' % (event.date, event.start_time, event.fosdem_id)
        try:
            self.app.data.insert('fosdem2020_favorite', sortkey, event.fosdem_id)
        except sqlite3.IntegrityError as exc:
            if not 'UNIQUE constraint failed' in str(exc):
                raise

    def remove_favorite(self, event):
        sortkey = '%s_%s_%s' % (event.date, event.start_time, event.fosdem_id)
        try:
            self.app.data.delete('fosdem2020_favorite', sortkey)
        except sqlite3.IntegrityError as exc:
            if not 'UNIQUE constraint failed' in str(exc):
                raise

    def open_note(self, event):
        self.app.change_view('notes', {
            'open': 'fosdem-2019/%s' % event.track[0:120],
        })

    def open_popup(self, event):
        self.popup_open = True
        self.original_widget = urwid.Overlay(
            urwid.LineBox(urwid.Filler(urwid.Text(event.description), 'top')),
            self.original_widget,

            align='center',
            valign='middle',

            width=('relative', 80),
            height=('relative', 80),
        )

    def keypress(self, size, key):
        if self.popup_open:
            if key == 'f':
                # TODO add favorite
                return
            if key in ['enter', 'q', 'Q']:
                self.original_widget = self.original_widget[0]
                self.popup_open = False
                return
        return super().keypress(size, key)

class FosdemPanes(urwid.Columns):
    def __init__(self, view, fosdem):
        self.view = view
        self.fosdem = fosdem
        self.tracklist = FosdemTrackList(self, fosdem)
        self.eventlist = FosdemEventList(self, [])

        super().__init__(
            [
                self.tracklist,
                self.eventlist,
            ]
        )

    def update_track(self, track, info=None):
        self.eventlist.change_track(track, *self.fosdem.get_track(track))

    def add_favorite(self, event):
        return self.view.add_favorite(event)

    def remove_favorite(self, event):
        return self.view.remove_favorite(event)

    def open_note(self, event):
        return self.view.open_note(event)

    def show_event_details(self, ev):
        self.view.open_popup(ev)

    def keypress(self, size, key):
        handled = self.focus.keypress(size, key) is None
        if handled:
            return
        if key == 'h':
            key = 'left'
        if key == 'l':
            key = 'right'
        return super().keypress(size, key)
