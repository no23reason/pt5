SHELL := /bin/bash

.PHONY: test
test:
	cd packages && $(MAKE) test
