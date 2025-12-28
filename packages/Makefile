SHELL := /bin/bash

PACKAGE_DIRS = pt5-core

.PHONY: test
test:
	for PKG in ${PACKAGE_DIRS}; do \
		$(MAKE) -C $${PKG} test || exit $$?; \
	done
