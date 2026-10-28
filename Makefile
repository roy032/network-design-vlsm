.PHONY: install build check test lint web serve all

install:  ## Install the package with dev tools
	pip install -e ".[dev]"

build:    ## Regenerate configs/ and docs/generated/ from network.toml
	vlsmkit build

check:    ## Fail if generated files are stale or LANs are unreachable
	vlsmkit check

test:     ## Python and JavaScript tests
	pytest
	node --test web/vlsm.test.mjs

lint:     ## Lint, format check and strict type check
	ruff check .
	ruff format --check .
	mypy

serve:    ## Run the web planner at http://localhost:8000
	python -m http.server 8000 --directory web

all: lint test check
