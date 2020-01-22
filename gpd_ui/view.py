import urwid

class View(urwid.Frame):
    def __init__(self, app, body, header=None, footer=None):
        self.app = app
        self._header = header
        self._body = body
        self._footer = footer

        super().__init__(
            header=self._header,
            body=self._body,
            footer=self._footer,
        )
