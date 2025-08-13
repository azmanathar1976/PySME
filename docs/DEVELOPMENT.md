# PySme Development Setup

## Requirements
- Python 3.13+
- pipx or Poetry
- Node.js (for Tailwind and WASM bundling)

## Setup
```bash
# Using pipx
pipx install poetry
poetry install

pip install poetry
poetry install

# Or directly
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
