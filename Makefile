all: check test

check:
	python -c 'import rudix'
	python -c 'from rudix import core, local, remote'
	python setup.py check

test:
	python -m unittest discover tests

build:
	python setup.py build

install:
	python setup.py install --user

upload:
	python setup.py sdist upload

clean:
	python setup.py clean
	rm -rf *~ *.ps *.pdf build dist rudix.egg-info
	rm -rf rudix/*~ rudix/*.pyc
