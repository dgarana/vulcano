.DEFAULT_GOAL := help

PYTHON := python
SRC     := vulcano

.PHONY: help fmt black isort lint flake8 security bandit test check all

help:           ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# ── Formatting ────────────────────────────────────────────────────────────────

fmt: black isort  ## Run all formatters (black + isort)

black:          ## Format code with black
	$(PYTHON) -m black $(SRC)

isort:          ## Sort imports with isort
	$(PYTHON) -m isort $(SRC)

# ── Linting ───────────────────────────────────────────────────────────────────

lint: flake8    ## Run all linters

flake8:         ## Check style with flake8
	$(PYTHON) -m flake8 $(SRC)

# ── Security ──────────────────────────────────────────────────────────────────

security: bandit  ## Run all security checks

bandit:         ## Scan for common security issues with bandit
	$(PYTHON) -m bandit -r $(SRC) -ll

# ── Tests ─────────────────────────────────────────────────────────────────────

test:           ## Run the test suite with pytest
	$(PYTHON) -m pytest $(SRC)

# ── Convenience ───────────────────────────────────────────────────────────────

check:          ## Run all checks without modifying files (CI-friendly)
	$(PYTHON) -m black --check $(SRC)
	$(PYTHON) -m isort --check-only $(SRC)
	$(PYTHON) -m flake8 $(SRC)
	$(PYTHON) -m bandit -r $(SRC) -ll

all: fmt check test  ## Format, check, and test everything
