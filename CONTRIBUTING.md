# Contributing to PySme

Thank you for your interest in contributing! 🚀

## Ways to Contribute
- **Report bugs** via GitHub Issues.
- **Request features** via GitHub Discussions.
- **Submit pull requests** for bug fixes or features.

## Workflow
1. Fork the repo.
2. Create a feature branch from `main`.
3. Commit changes following Conventional Commits.
4. Open a Pull Request (PR).

## Review Process
- All PRs require at least 1 maintainer approval.
- Changes to `/pysme` or `/src/compiler` require 2 approvals.
- CI must pass before merge.

## Setup for Development
```bash
# Clone repo
git clone https://github.com/yourname/pysme.git
cd pysme

# Setup Python environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements-dev.txt

# Setup Rust environment
rustup default stable
cargo install cargo-watch
