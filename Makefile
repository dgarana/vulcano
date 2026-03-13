.DEFAULT_GOAL := help

UV_LINT := uv run --group lint
UV_TEST := uv run --group test
SRC     := vulcano

.PHONY: help fmt black isort lint flake8 security bandit test check all

help:           ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# ── Formatting ────────────────────────────────────────────────────────────────

fmt: black isort  ## Run all formatters (black + isort)

black:          ## Format code with black
	$(UV_LINT) black $(SRC)

isort:          ## Sort imports with isort
	$(UV_LINT) isort $(SRC)

# ── Linting ───────────────────────────────────────────────────────────────────

lint: flake8    ## Run all linters

flake8:         ## Check style with flake8
	$(UV_LINT) flake8 $(SRC)

# ── Security ──────────────────────────────────────────────────────────────────

security: bandit  ## Run all security checks

bandit:         ## Scan for common security issues with bandit
	$(UV_LINT) bandit -r $(SRC) -ll

# ── Tests ─────────────────────────────────────────────────────────────────────

test:           ## Run the test suite with pytest
	$(UV_TEST) pytest $(SRC)

# ── Convenience ───────────────────────────────────────────────────────────────

check:          ## Run all checks without modifying files (CI-friendly)
	$(UV_LINT) black --check $(SRC)
	$(UV_LINT) isort --check-only $(SRC)
	$(UV_LINT) flake8 $(SRC)
	$(UV_LINT) bandit -r $(SRC) -ll

all: fmt check test  ## Format, check, and test everything
