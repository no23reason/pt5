SHELL := /bin/bash

PACKAGE_DIRS = packages/pt5-core packages/pt5-gui

.PHONY: dev
dev:
	uv sync --all-groups

.PHONY: build
build:
	$(MAKE) -C packages/pt5-gui build

.PHONY: compile-messages
compile-messages:
	$(MAKE) -C packages/pt5-gui compile-messages

.PHONY: test
test:
	for PKG in ${PACKAGE_DIRS}; do \
		$(MAKE) -C $${PKG} test || exit $$?; \
	done

.PHONY: gui
gui:
	uv run --package pt5-gui packages/pt5-gui/src/pt5_gui/main.py

.PHONY: lint
lint:
	uv run ruff check

.PHONY: lint-fix
lint-fix:
	uv run ruff check --fix

.PHONY: format
format:
	uv run ruff format
