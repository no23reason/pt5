SHELL := /bin/bash

.PHONY: dev
dev: ;

.PHONY: test
test:
	uv run pytest

.PHONY: update-snapshots
update-snapshots:
	uv run pytest --snapshot-update
