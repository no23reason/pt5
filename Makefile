SHELL := /bin/bash

PACKAGE_DIRS = packages/pt5-core packages/pt5-gui

.PHONY: test
test:
	for PKG in ${PACKAGE_DIRS}; do \
		$(MAKE) -C $${PKG} test || exit $$?; \
	done

.PHONY: gui
gui:
	uv run --package pt5-gui packages/pt5-gui/src/pt5_gui/main.py
