DESTDIR?=/
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin
MANDIR=$(PREFIX)/share/man
DOCDIR=$(PREFIX)/share/doc/rudix
PYTHON_SITE_PACKAGES=$(shell python -c 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')

test:
	python -c 'import rudix'
	python tests.py

rudix.pdf: rudix.1
	groff  -Tps  -mandoc -c rudix.1 > rudix.ps
	pstopdf rudix.ps -o rudix.pdf

all: rudix.pdf test

build: rudix.py
	python setup.py build

install: test rudix.pdf build
	python setup.py install \
		--root=$(DESTDIR) \
		--prefix=$(PREFIX) \
		--install-lib=$(PYTHON_SITE_PACKAGES)
	install -d $(DESTDIR)/$(MANDIR)/man1
	install -m 644 rudix.1 $(DESTDIR)/$(MANDIR)/man1/rudix.1
	install -d $(DESTDIR)/$(DOCDIR)
	install -m 644 rudix.pdf $(DESTDIR)/$(DOCDIR)

upload:
	python setup.py sdist upload

uninstall:
	rm -f $(BINDIR)/rudix
	rm -f $(MANDIR)/man1/rudix.1
	rm -f $(DOCDIR)/rudix.pdf
	rm -rf $(PYTHON_SITE_PACKAGES)/rudix*

clean:
	python setup.py clean
	rm -rf *~ *.pyc *.ps *.pdf build dist MANIFEST
