GLAM rewrite - minimal scaffold

This repository is a clean rewrite scaffold for the original GLAM project.

Quickstart

Create a virtualenv and install test deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pytest pydantic
```

Run tests:

```bash
pytest
```

Structure

- src/glam: package code
- tests: pytest tests
