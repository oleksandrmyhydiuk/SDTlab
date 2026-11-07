# Python Validator Class

This project is part of a lab assignment for the "Software Development Tools" course.

It is a small but powerful `Validator` class in Python, designed for validating input data. Unlike a simple set of functions, this validator uses an object-oriented approach, collects errors, and supports method chaining.

## 🚀 Key Features

  * **Method Chaining:** Validation methods can be called one after another on the same object.
  * **Error Collection:** The validator collects a comprehensive list of all issues instead of stopping
    at the first one.
  * **Type Checking:** Automatically checks if the data type matches the expected type.
  * **Flexible Validation:** Allows specifying parameters like a required email domain or a phone's
    country code.
  * **Custom Messages:** Allows specifying custom error messages for each validation rule.

## 🛠️ How to Use

### Code Example:

```python
from validator import Validator

# --- Example 1: Successful Validation ---
v1 = Validator("test@example.com").is_not_empty().is_email()
print(v1.is_valid())  # Outputs: True

# --- Example 2: Failed Validation (Error Collection) ---
v2 = Validator("weak-pass").is_strong_password()
print(v2.is_valid())  # Outputs: False
print(v2.get_errors())
# Outputs: ['Password is not strong: ...']

# --- Example 3: Failure due to Wrong Type ---
v3 = Validator(12345).is_email()
print(v3.is_valid())  # Outputs: False
print(v3.get_errors())
# Outputs: ['Value must be of type str, got int']

# --- Example 4: New Features (Domain & Country Code) ---
# Check if email belongs to @corporate.com
v4_email = Validator("user@gmail.com").is_email(required_domain="corporate.com")
print(v4_email.is_valid()) # Outputs: False
print(v4_email.get_errors()) # Outputs: ['Email must be from domain @corporate.com']

# Check a UA phone number
v4_phone = Validator("+380123456789").is_phone(country_code="+380")
print(v4_phone.is_valid()) # Outputs: True
```

## 📋 Available Validation Methods

  * `.is_type(expected_type, [message])`: Checks if the value is an instance of `expected_type`.
  * `.is_not_empty([message])`: Checks if a string is not `None` and does not consist only of
    whitespace.
  * `.is_in_range(min_val, max_val, [message])`: Checks if a number is within the range
    `[min_val, max_val]`.
  * `.is_email(required_domain=None, [message])`: Checks if the string matches an email format. If `required_domain` is provided, it also validates the domain.
  * `.is_strong_password([min_len=8], [message])`: Checks password complexity.
  * `.matches_regex(pattern, [message])`: Checks the string against a provided regex pattern.
  * `.is_phone(country_code=None, [message])`: Checks a phone number. If `country_code` is set (e.g., `"+380"`), it enforces that prefix. If `None`, it checks for a generic `+...digits...` format.

## 🧪 Testing

The project includes a comprehensive unit test suite using `pytest`. The tests cover basic logic, edge cases, error handling, and the new validation features.

To run the tests:

```bash
pip install pytest
pytest
```

## 📚 Documentation

Detailed API documentation is automatically generated using Doxygen + doxypypy and published via GitHub Pages.

**[View Live Documentation](https://oleksandrmyhydiuk.github.io/SDTlab/)**

