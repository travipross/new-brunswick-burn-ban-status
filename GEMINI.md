# Agent Instructions

## Mandatory Validation

To maintain the technical integrity of this integration, you MUST run the following quality checks after every functional change:

1. **Linting & Formatting:**
   Ensure the code adheres to the project's style and passes all linting rules.

   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   ```

2. **Unit Tests:**
   Ensure no regressions were introduced by running the full test suite.
   ```bash
   uv run pytest
   ```

## Development Workflow

- **Dependency Management:** Use `uv` for all local development tasks.
- **Environment Setup:** If new dependencies are added, run `uv sync --dev`.
- **Testing:** All core logic (coordinator, helpers, constants) should have corresponding tests in the `tests/` directory.
- **Committing:** Follow conventional commit format, with appropriate prefixes for commit short messages. Add extra detail as multi-line content where appropriate

## Shell Commands

- **Non-interactive Pager** Always be sure to avoid interactive pagers (e.g. `less`) which may be set by default in the shell. Use something non-interactive such as `less` when calling commands that typically output to a pager.
- \*\*This project is hosted on GitHub, and you can consider the `gh` CLI to be available for shell commands.
  - When calling `gh` commands, always confirm with the developer before executing anything beyond "read-only" commands. You can fetch information like job logs, PR descriptsions, issues, etc. without necessarily confirming, but never create new PRs, issues, etc without explicit approval by the developer.
