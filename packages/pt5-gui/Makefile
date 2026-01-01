SHELL := /bin/bash

.PHONY: test
test:
	echo "no tests yet"

.PHONY: compile-messages
compile-messages:
	for po in $$(find src/pt5_gui/locales -name "*.po"); do \
		msgfmt -o "$${po%.po}.mo" "$$po"; \
	done

.PHONY: build
build:
	cd src/pt5_gui && uv run pyinstaller main.spec
