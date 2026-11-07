# Python Validator (`SDTlab`)

[![Deploy Doxygen Docs](https://github.com/oleksandrmyhydiuk/SDTlab/actions/workflows/docs.yml/badge.svg)](https://github.com/oleksandrmyhydiuk/SDTlab/actions/workflows/docs.yml)
[![Run Unit Tests](https://github.com/oleksandrmyhydiuk/SDTlab/actions/workflows/tests.yml/badge.svg)](https://github.com/oleksandrmyhydiuk/SDTlab/actions/workflows/tests.yml)
[![Live Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://oleksandrmyhydiuk.github.io/SDTlab/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A lightweight, zero-dependency, object-oriented data validation library in Python developed as part of the **"Software Development Tools"** (*Інструментальні засоби розробки програмного забезпечення*) course.

Unlike procedural validation functions that fail on the first error or raise exceptions immediately, `Validator` is **stateful**, supports **fluent method chaining**, safely short-circuits on `None` or invalid data types, and **accumulates all validation errors** in a single pass.

---

## Key Features

- **Fluent Method Chaining:** Chain multiple validation rules sequentially on a single `Validator` instance.
- **Comprehensive Error Collection:** Collects every validation failure across the chain instead of stopping at the first logical error.
- **Type-Safe Short-Circuiting:** Automatically verifies data types (including distinguishing `bool` from numeric `int`/`float`) and stops further checks when a type mismatch or `None` is encountered to prevent runtime `TypeError` or `AttributeError`.
- **Flexible Domain & Country Rules:** Supports case-insensitive email domain enforcement (`required_domain`) and country-specific or generic E.164 phone number validation (`country_code`).
- **Custom Error Messages:** Override default error messages per rule for localized or user-friendly feedback.
- **Automated CI/CD & Documentation:** Tested with `pytest` and documented with **Doxygen + doxypypy**, automatically deployed to GitHub Pages via GitHub Actions.

---

## Project Structure

```text
SDTlab/
├── .github/
│   └── workflows/
│       ├── docs.yml          # CI/CD workflow for Doxygen build & GitHub Pages deployment
│       └── tests.yml         # CI workflow for running pytest unit tests
├── etc/                      # Course lab reports (.docx)
├── test/
│   ├── README.md             # Testing methodology & parametrization overview
│   └── test_validator.py     # Comprehensive pytest unit test suite (34 test cases)
├── Doxyfile                  # Doxygen configuration (with doxypypy filter)
├── LICENSE                   # MIT License
├── pytest.ini                # Pytest configuration
├── README.md                 # Project documentation
├── SECURITY.md               # Security policy & vulnerability reporting
└── validator.py              # Core Validator implementation
```

---

## Getting Started

### Prerequisites

- **Python 3.10+** (uses modern union type hints `str | None`)
- **`pytest`** (for running the test suite)

### Installation

Clone the repository and (optionally) set up a virtual environment:

```bash
git clone https://github.com/oleksandrmyhydiuk/SDTlab.git
cd SDTlab

python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install pytest
```

---

## How to Use

### Code Examples

```python
from validator import Validator

# 1. Successful validation with method chaining
v1 = Validator("user@example.com").is_not_empty().is_email()
print(v1.is_valid())      # True
print(v1.get_errors())    # []

# 2. Error accumulation across multiple rules
v2 = Validator("weak").is_strong_password()
print(v2.is_valid())      # False
print(v2.get_errors())
# ['Password is not strong: must be at least 8 characters, must contain one uppercase letter, must contain one digit, must contain one special symbol']

# 3. Safe short-circuiting on wrong type or None
v3 = Validator(12345).is_not_empty().is_email()
print(v3.is_valid())      # False
print(v3.get_errors())    # ['Value must be of type str, got int']

# 4. Email validation with required domain (case-insensitive)
v4 = Validator("employee@gmail.com").is_email(required_domain="corporate.com")
print(v4.is_valid())      # False
print(v4.get_errors())    # ['Email must be from domain @corporate.com']

# 5. Phone validation with country code & custom error message
v5 = Validator("+380991234567").is_phone(
    country_code="+380",
    message="Введіть коректний український номер (+380...)"
)
print(v5.is_valid())      # True

# 6. Numeric range validation (inclusive)
v6 = Validator(42).is_in_range(0, 100)
print(v6.is_valid())      # True
```

---

## Available Validation Methods

| Method | Parameters | Description |
| :--- | :--- | :--- |
| `Validator(value)` | `value: Any` | Initializes a stateful validator for `value`. Immediately records an error and halts further checks if `value is None`. |
| `.is_valid()` | — | Returns `True` if no validation errors were recorded, `False` otherwise. |
| `.get_errors()` | — | Returns `list[str]` containing all collected error messages. |
| `.is_type(expected_type, message=None)` | `expected_type: type`, `message: str \| None` | Checks `isinstance(value, expected_type)` (excluding `bool` for non-`bool` types). Stops subsequent checks on failure. |
| `.is_not_empty(message=None)` | `message: str \| None` | Verifies the value is a `str` and contains non-whitespace characters. |
| `.is_in_range(min_val, max_val, message=None)` | `min_val: Number`, `max_val: Number`, `message: str \| None` | Verifies the value is a number (`numbers.Number`, excluding `bool`) within `[min_val, max_val]` inclusive. |
| `.is_email(required_domain=None, message=None)` | `required_domain: str \| None`, `message: str \| None` | Validates email format and optionally enforces a specific domain (case-insensitive, with or without `@` prefix). |
| `.is_strong_password(min_len=8, message=None)` | `min_len: int = 8`, `message: str \| None` | Checks minimum length, uppercase, lowercase, digit, and special character (`@$!%*?&#`), reporting all missing criteria at once. |
| `.matches_regex(pattern, message=None)` | `pattern: str \| re.Pattern`, `message: str \| None` | Checks whether the string matches the given regular expression pattern. |
| `.is_phone(country_code=None, message=None)` | `country_code: str \| None`, `message: str \| None` | Validates a phone number with an enforced `country_code` prefix (e.g. `"+380"`) or generic `+[digits]` format. |

---

## Testing

The project includes a comprehensive `pytest` suite in [`test/test_validator.py`](test/test_validator.py) (34 test cases using `@pytest.mark.parametrize`) covering:
- Valid and invalid method chains
- Multiple error accumulation
- Type mismatch and `None` short-circuiting (including `bool` vs `Number`)
- Boundary conditions for `.is_in_range()`
- Individual criteria and multi-error reporting for `.is_strong_password()`
- Custom error messages
- Specific country codes and email domain constraints

Run all tests from the project root:

```bash
pytest -v
```

See [`test/README.md`](test/README.md) for a detailed overview of the testing strategy.

---

## Documentation

API documentation is generated from Doxygen-annotated docstrings using **Doxygen** and **doxypypy**, and automatically deployed to GitHub Pages on push via [`.github/workflows/docs.yml`](.github/workflows/docs.yml).

**[View Live Documentation](https://oleksandrmyhydiuk.github.io/SDTlab/)**

To generate the documentation locally:

```bash
pip install doxypypy
doxygen Doxyfile
```

The generated HTML site will be placed in `docs_doxygen/html/index.html`.

---

## Security

Please review [`SECURITY.md`](SECURITY.md) for information on supported versions, security design principles, and how to report vulnerabilities responsibly.

---

## License

This project is licensed under the **MIT License** — see the [`LICENSE`](LICENSE) file for details.
