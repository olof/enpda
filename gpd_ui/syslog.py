import urwid
from gpd_ui.view import View

class SyslogView(View):
    def __init__(self, app, logpath='/var/log/syslog', **kwargs):
        self.logpath = logpath
        lines = self.read_syslog()
        self._syslog = urwid.ListBox([urwid.Text(line.strip()) for line in lines])
        super().__init__(app=app, body=self._syslog)
        self._syslog.set_focus(len(self._syslog.body)-1)

    def read_syslog(self):
        with open('/var/log/syslog') as fh:
            return fh.readlines()
