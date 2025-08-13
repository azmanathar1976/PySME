@echo off
echo Running lint and type checks...
poetry run pre-commit run --all-files
poetry run mypy pysme
poetry run pyright
echo Running tests...
poetry run pytest tests/
