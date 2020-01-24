import re
import urwid
from enpda.view import View

class SyslogLine:
    line_pattern = re.compile(r'''
        (?P<date>\S+\s+\S+) \s+ (?P<time>\S+) \s+
        (?P<hostname>\S+) \s+
        (?P<service>[A-Za-z0-9/_.-]+)(?:\[\d+\])?:
        (?P<msg>.*)
    ''', re.X)

    def __init__(self, line):
        self.line = line
        self.parse()

    def parse(self):
        m = self.line_pattern.match(self.line)
        if m:
            self.date = m.group('date')
            self.time = m.group('time')
            self.hostname = m.group('hostname')
            self.service = m.group('service')
            self.msg = m.group('msg')
        else:
            self.date = '???'
            self.time = '???'
            self.hostname = 'unknown'
            self.service = 'unknown'
            self.msg = 'unparsed line: %s' % self.line

    def __str__(self):
        return self.line

class SyslogView(View):
    def __init__(self, app, logpath='/var/log/syslog', **kwargs):
        self.logpath = logpath
        lines = self.read_syslog()
        self._syslog = urwid.ListBox(
            urwid.SimpleFocusListWalker([self.make_line(l) for l in lines])
        )
        super().__init__(app=app, body=self._syslog)
        self._syslog.set_focus(len(self._syslog.body)-1)

    def make_line(self, line):
        entry = SyslogLine(line.strip())
        cols = [
            (15, urwid.Text('%s %s' % (entry.date, entry.time))),
            (16, urwid.Text(entry.service)),
            urwid.Text(entry.msg),
        ]
        return urwid.Columns(cols, dividechars=2)

    def read_syslog(self):
        with open('/var/log/syslog') as fh:
            return fh.readlines()
