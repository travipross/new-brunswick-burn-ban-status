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
