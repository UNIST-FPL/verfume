## Running the Application

### Setup

Install [uv](https://docs.astral.sh/uv/) if you don't have it, then install the project:

```bash
pip install uv       # or: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --extra optional
```

### Launch

```bash
# Open the GUI (empty, no file loaded)
uv run python main.py

# Open the GUI with a gEQDSK file loaded immediately
uv run python main.py examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk
```

The application window will open. Use **File → Open gEQDSK** (or `Ctrl+O`) to load an
equilibrium file if you did not pass one on the command line.

---

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
# During development — skip slow tests for a fast feedback loop
uv run pytest tests/ -v -m "not slow"

# Before opening a pull request — run the full suite including slow tests
uv run pytest tests/ -v

# Run a single test module
uv run pytest tests/test_geqdsk_parser.py -v

# Generate an HTML coverage report (opens at htmlcov/index.html)
uv run pytest tests/ --cov=mesh_gui_project --cov-report=html
```

> **Before submitting a pull request**, run the full suite (`uv run pytest tests/ -v`,
> including slow tests) locally and confirm all tests pass.
>
> Note: the CI workflow runs only the non-slow subset (`-m "not slow"`) to keep
> build times short. Slow tests are **not** verified by CI, so they are your
> responsibility to run locally before requesting a review.
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
