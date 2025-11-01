## Testing

To ensure the reliability and correctness of the `Validator` class, a comprehensive suite of unit tests was created using the **Pytest** framework.

### 🎯 Key Aspects Covered by Tests:

1.  **State Correctness:** Verifying that the `.is_valid()` method returns `True` only when no checks have failed, and `False` otherwise.
2.  **Accurate Error Collection:** Tests ensure that the `.get_errors()` method returns the precise list of error messages that occurred during validation.
3.  **Method Chaining:** Specific tests check scenarios where multiple validation methods are called sequentially (e.g., `.is_not_empty().is_email()`).
4.  **Handling Invalid Types:** Tests guarantee that the validator reacts correctly to unexpected data types (like trying to check an `int` as an email) and stops further checks.
5.  **Flexible Validation:** Dedicated tests verify the new features:
      * Correct email validation with `required_domain` (including case-insensitivity checks).
      * Correct `is_phone` validation both with a `country_code` and without (generic format).
6.  **Custom Messages:** Tests check that user-supplied error messages (`message=...`) are correctly reflected in the final error list.

### ✨ Key Feature: Parametrization

The **`@pytest.mark.parametrize`** decorator is used extensively to efficiently test edge cases and exceptions.

This allows us to run a single test function with dozens of different inputs without duplicating code. Instead of writing 7 separate test functions for the password, we define 7 scenarios:

*Example of parametrization for `is_strong_password`:*

```python
@pytest.mark.parametrize("password, expected_valid, contains_error", [
    ("P@ssword123", True, None),        # Base case: valid
    ("P@s1", False, "at least 8 characters"), # Edge case: too short
    ("p@ssword123", False, "one uppercase letter"), # Edge case: no uppercase
    ("P@SSWORD123", False, "one lowercase letter"), # Edge case: no lowercase
    ("P@sswordABC", False, "one digit"),      # Edge case: no digit
    ("Password123", False, "one special symbol"), # Edge case: no special char
    ("weak", False, "at least 8 characters"), # Case: multiple errors
])
def test_is_strong_password(password, expected_valid, contains_error):
    """This single test will check all 7 password scenarios."""
    v = Validator(password).is_strong_password()
    assert v.is_valid() is expected_valid
    if not expected_valid:
        # Check that the error message contains the expected reason
        assert contains_error in v.get_errors()[0]
```

Thanks to this approach, the **20+ test functions** in the `test_validator_v2.py` file actually execute **over 30 unique test scenarios**, fully covering the validator's logic.

### ⚙️ How to Run Tests

1.  Install `pytest`:
    ```bash
    pip install pytest
    ```
2.  From the project's root directory, run the command:
    ```bash
    pytest
    ```
