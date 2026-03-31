# AGENTS.md

## Project purpose

Vulcano is a framework for building command-line utilities in Python.
Its main goal is to simplify command creation by reusing already existing Python functions and exposing them through an interactive CLI or argument-based interface.

## Project vision

This project aims to be community-driven and significantly supported by AI-assisted development. Contributors should be able to propose ideas and improvements in plain text, and AI agents may help translate those ideas into code contributions.

All contributions must remain aligned with the core purpose of the project and should not drift away from the goal of making Python command-line utility creation simpler and more reusable.

## Working rules for AI agents

- Stay aligned with the core CLI-framework purpose of the repository.
- Prefer small, focused changes over broad speculative refactors.
- Update documentation when behavior, public APIs, or workflows change.
- Use conventional commit messages such as `fix:`, `feat:`, `docs:`, `test:`, `refactor:`, and `chore:`.
- Pull requests should explain scope clearly and link related issues when applicable.

## Quality guardrails

Before considering a task complete, contributors and AI agents should ensure:

- lint checks pass
- relevant documentation is updated when needed
- there is specific test coverage for the modified or newly introduced behavior

The intent is to avoid changes that work only superficially while leaving documentation, tests, or repository conventions behind.
