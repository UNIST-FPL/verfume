## Running Tests

This project ships with a test suite under `tests/`. All contributors are expected to run the full test suite before submitting a pull request and ensure every test passes.

### Setup

Install [uv](https://docs.astral.sh/uv/) if you don't have it, then sync the project with development dependencies:

```bash
pip install uv       # or: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --extra dev --extra optional
```

### Run the tests

```bash
# Run the full test suite — required before opening a pull request
uv run pytest tests/ -v

# Skip slow tests for a faster feedback loop during development
uv run pytest tests/ -v -m "not slow"

# Run a single test module
uv run pytest tests/test_geqdsk_parser.py -v

# Generate an HTML coverage report (opens at htmlcov/index.html)
uv run pytest tests/ --cov=mesh_gui_project --cov-report=html
```

> **Before submitting a pull request**, run `uv run pytest tests/ -v` and confirm all tests pass.
> Pull requests with failing tests will not be merged.

---

## 📜 License & Commercial Use

This project is licensed under the terms of the **GNU Affero General Public License v3.0 (AGPL-3.0)**. 

### ⚠️ Important Notice for Commercial Users
While this software is provided as open-source, the following restrictions apply to protect the project's sustainability:

* **Commercial Use:** If you wish to use this software for commercial purposes, or incorporate it into a proprietary service (SaaS) without disclosing your entire system's source code under AGPL v3, **a separate commercial license is required.**
* **Modified Versions:** Distribution of modified versions of this software requires prior written permission if the intended use falls outside the standard AGPL v3 permissions.
* **Academic & Personal Use:** Free use is encouraged for academic research and personal, non-commercial projects, provided that the terms of the AGPL v3 are met.

For all licensing inquiries, commercial partnership proposals, or permission requests, please contact:
📧 **esyoon@unist.ac.kr**
