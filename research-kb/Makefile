# Local operator entry points for the shared research KB.
#
# `make setup` is the one-command path: install, register every agent client,
# and build the catalog. See scripts/setup-mcp.sh for the flags.

PYTHON ?= .venv/bin/python
KB ?= .venv/bin/research-kb
HOME_DIR ?= $(HOME)/.local/share/research-kb
CONFIG ?= $(HOME)/.config/research-kb/sources.toml

.PHONY: help setup setup-watch clients verify refresh status search test lint update-sources

help:
	@echo "setup"
	@echo "  make setup          install, refresh, register all clients (stdio)"
	@echo "  make setup-watch    same, plus a launchd/systemd freshness watcher"
	@echo "  make clients        re-register clients only"
	@echo ""
	@echo "operate"
	@echo "  make refresh        rebuild the catalog from registered sources"
	@echo "  make status         coverage, revision and last refresh"
	@echo "  make search Q=...   search the shared corpus"
	@echo "  make verify         catalog -> CLI -> real MCP subprocess -> configs"
	@echo ""
	@echo "develop"
	@echo "  make test           full test suite"
	@echo "  make lint           ruff check and format check"

setup:
	./scripts/setup-mcp.sh

setup-watch:
	./scripts/setup-mcp.sh --watch

clients:
	$(KB) install-client --client all --command "$(CURDIR)/$(KB)"

refresh:
	RESEARCH_KB_HOME=$(HOME_DIR) RESEARCH_KB_CONFIG=$(CONFIG) $(KB) refresh

update-sources:
	RESEARCH_KB_HOME=$(HOME_DIR) RESEARCH_KB_CONFIG=$(CONFIG) $(KB) update-sources

status:
	RESEARCH_KB_HOME=$(HOME_DIR) RESEARCH_KB_CONFIG=$(CONFIG) $(KB) status

search:
	@test -n "$(Q)" || (echo "usage: make search Q='query'" && exit 1)
	RESEARCH_KB_HOME=$(HOME_DIR) RESEARCH_KB_CONFIG=$(CONFIG) $(KB) search "$(Q)"

verify:
	RESEARCH_KB_HOME=$(HOME_DIR) RESEARCH_KB_CONFIG=$(CONFIG) $(PYTHON) scripts/verify_mcp.py

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check src/research_kb tests
	$(PYTHON) -m ruff format --check src/research_kb tests
