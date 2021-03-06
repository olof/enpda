NAME = enpda
DATADIR ?= $(PREFIX)/share
VARDIR ?= /var/lib/$(NAME)
BINDIR ?= $(PREFIX)/bin
APPDIR ?= $(DATADIR)/$(NAME)

FOSDEM_XML_NAME = fosdem.xml
FOSDEM_XML_FETCH_PROG = curl -o "$(FOSDEM_XML_NAME)" -L
FOSDEM_XML_FETCH_URL = https://fosdem.org/2020/schedule/xml

all:
clean:

fosdem.xml:
	$(FOSDEM_XML_FETCH_PROG) "$(FOSDEM_XML_FETCH_URL)"

install:
	install -d $(DESTDIR)$(BINDIR)
	install -d $(DESTDIR)$(APPDIR)
	install -d $(DESTDIR)$(VARDIR)
	find $(NAME) -type d \( \( -name __pycache__ -prune \) -o -exec install -d $(DESTDIR)$(APPDIR)/{} \; \)
	find $(NAME) \( -name __pycache__ -prune \) -o -type f -exec install {} $(DESTDIR)$(APPDIR)/{} \;
	install -m 0755 bin/enpda $(DESTDIR)$(BINDIR)/enpda

.PHONY: all clean install
