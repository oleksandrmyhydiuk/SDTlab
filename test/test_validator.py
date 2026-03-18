"""
@file test_validator.py
@brief Unit tests for the Validator class with detailed scenario descriptions.

This module contains a comprehensive suite of tests for the Validator class.
It uses the pytest framework to verify:
- Basic validation logic and method chaining.
- Error collection and reporting mechanisms.
- Handling of edge cases (None, invalid types).
- Advanced features like specific domain validation and country codes.
"""

import pytest
from validator import Validator


# --- 1. Base Logic and Chaining Tests ---

def test_valid_chain_email():
    """
    Tests a successful validation chain for a valid email.

    This test verifies that chaining multiple methods (.is_not_empty() and .is_email())
    on a valid input string results in a valid state (is_valid() returns True)
    and an empty error list.
    """
    v = Validator("test@example.com").is_not_empty().is_email()
    assert v.is_valid() is True
    assert v.get_errors() == []


def test_valid_chain_number():
    """
    Tests a successful validation chain for a number within a range.

    Verifies that a numeric value satisfying the range condition passes validation.
    This confirms that the validator correctly handles numeric types.
    """
    v = Validator(10).is_in_range(5, 15)
    assert v.is_valid() is True
    assert v.get_errors() == []


def test_chain_fail_at_first_step():
    """
    Tests that the chain correctly captures failure at the very first step.

    Scenario: Input is whitespace.
    The first check (.is_not_empty) should fail.
    We verify that the error list contains the specific message regarding empty values.
    """
    v = Validator("  ").is_not_empty().is_email()
    assert v.is_valid() is False
    assert any("Value cannot be empty" in e for e in v.get_errors())


def test_chain_fail_at_second_step():
    """
    Tests that the chain continues to the second step if the first passes, and captures failure there.

    Scenario: Input is not empty (passes step 1), but is not a valid email (fails step 2).
    We verify that the error relates to the email format.
    """
    v = Validator("not-an-email").is_not_empty().is_email()
    assert v.is_valid() is False
    assert any("Invalid email format" in e for e in v.get_errors())


def test_chain_multiple_errors():
    """
    Tests the accumulation of multiple errors in a single chain.

    Scenario: The input fails BOTH the email check and the strong password check.
    The validator should not stop after the first logical failure (unlike type errors).
    We verify that the error list contains at least 2 messages, covering both failures.
    """
    v = Validator("not-an-email").is_email().is_strong_password()
    assert v.is_valid() is False
    assert len(v.get_errors()) >= 2
    assert any("Invalid email format" in e for e in v.get_errors())
    assert any("Password is not strong" in e for e in v.get_errors())


def test_stop_validation_on_type_error():
    """
    Tests the critical safety mechanism: stopping validation on type mismatch.

    Scenario: An integer is passed to methods expecting a string (.is_not_empty, .is_email).
    The validator must detect the type mismatch immediately and STOP further checks
    to prevent a runtime `AttributeError` or `TypeError` in subsequent methods.
    We expect exactly one error message about the invalid type.
    """
    v = Validator(12345).is_not_empty().is_email()
    assert v.is_valid() is False
    assert len(v.get_errors()) == 1
    assert any("Value must be of type str" in e for e in v.get_errors())


def test_none_input():
    """
    Tests the handling of `None` as an input value.

    Scenario: Validator is initialized with None.
    This is a fundamental edge case. The validator should immediately flag this as an error
    and refuse to perform further checks to avoid crashing.
    """
    v = Validator(None)
    assert v.is_valid() is False
    assert len(v.get_errors()) == 1
    assert any("Value cannot be None" in e for e in v.get_errors())

    # Verify that calling more methods doesn't add more errors or crash
    v.is_email().is_not_empty()
    assert len(v.get_errors()) == 1, "Subsequent methods should be skipped for None input"


# --- 2. Parametrized Tests for Individual Methods ---

@pytest.mark.parametrize("value, expected_valid", [
    (10, True),  # Valid: Value is inside the range
    (0, True),  # Boundary: Value equals min_val
    (100, True),  # Boundary: Value equals max_val
    (-1, False),  # Invalid: Value is strictly less than min_val
    (101, False),  # Invalid: Value is strictly greater than max_val
])
def test_is_in_range(value, expected_valid):
    """
    Parametrized test for the .is_in_range() method covering boundaries.

    This test runs multiple times with different inputs to verify:
    1. Normal values inside the range.
    2. Exact boundary values (inclusive check).
    3. Values just outside the boundaries.

    @param value The numeric value to test.
    @param expected_valid The expected boolean result of the validation.
    """
    v = Validator(value).is_in_range(0, 100)
    assert v.is_valid() is expected_valid
    if not expected_valid:
        assert any("must be between 0 and 100" in e for e in v.get_errors())


@pytest.mark.parametrize("password, expected_valid, contains_error", [
    ("P@ssword123", True, None),  # Valid: Meets all criteria
    ("P@s1", False, "at least 8 characters"),  # Invalid: Too short
    ("p@ssword123", False, "one uppercase letter"),  # Invalid: Missing uppercase
    ("P@SSWORD123", False, "one lowercase letter"),  # Invalid: Missing lowercase
    ("P@sswordABC", False, "one digit"),  # Invalid: Missing digit
    ("Password123", False, "one special symbol"),  # Invalid: Missing special char
    ("weak", False, "at least 8 characters"),  # Invalid: Multiple flaws
])
def test_is_strong_password(password, expected_valid, contains_error):
    """
    Parametrized test for .is_strong_password() verifying all security criteria.

    This checks each rule of the strong password policy individually:
    - Length requirement.
    - Character set requirements (upper, lower, digit, symbol).

    @param password The password candidate.
    @param expected_valid Expected result.
    @param contains_error A text substring that must appear in the error message if invalid.
    """
    v = Validator(password).is_strong_password()
    assert v.is_valid() is expected_valid
    if not expected_valid:
        assert len(v.get_errors()) > 0
        assert any(contains_error in e for e in v.get_errors())


def test_password_multiple_failings():
    """
    Tests that the password validator reports ALL missing criteria, not just the first one.

    Scenario: A password is "weak". It is short, has no uppercase, no digits, etc.
    The error message should contain specific warnings for ALL these failures simultaneously.
    This ensures the user gets full feedback in one go.
    """
    v = Validator("weak").is_strong_password()
    assert v.is_valid() is False

    # Combine all errors into one string for easier substring checking
    combined_errors = " ".join(v.get_errors())

    assert "at least 8 characters" in combined_errors
    assert "one uppercase letter" in combined_errors
    assert "one digit" in combined_errors
    assert "one special symbol" in combined_errors


# --- 3. Custom Message Tests ---

def test_custom_error_message_is_not_empty():
    """
    Tests the ability to override the default error message for .is_not_empty().

    This verifies that if the user provides a `message` argument,
    the validator stores EXACTLY that message instead of the default one.
    """
    custom_msg = "Email є обов'язковим полем"
    v = Validator("").is_not_empty(message=custom_msg)
    assert v.is_valid() is False
    assert v.get_errors() == [custom_msg]


def test_custom_error_message_is_phone():
    """
    Tests custom error messages for the .is_phone() method.

    Verifies that custom feedback works even when the validation logic uses
    complex internal regex generation (like with country codes).
    """
    custom_msg = "Введіть коректний номер +380"
    v = Validator("12345").is_phone(country_code="+380", message=custom_msg)
    assert v.is_valid() is False
    assert v.get_errors() == [custom_msg]


def test_custom_error_message_is_email_domain():
    """
    Tests custom error messages for specific email domain validation failures.

    Verifies that the custom message overrides the default "Email must be from domain..." message.
    """
    custom_msg = "Дозволені лише корпоративні адреси"
    v = Validator("user@gmail.com").is_email(required_domain="corp.com", message=custom_msg)
    assert v.is_valid() is False
    assert v.get_errors() == [custom_msg]


# --- 4. New Feature Tests (Domains and Country Codes) ---

def test_is_phone_with_specific_country_code_pass():
    """
    Tests that .is_phone() correctly validates a number matching a specific country code.

    Scenario: Country code is set to "+48". Input starts with "+48".
    Result should be valid.
    """
    v = Validator("+48123456789").is_phone(country_code="+48")
    assert v.is_valid() is True


def test_is_phone_with_specific_country_code_fail():
    """
    Tests that .is_phone() fails if the number does not start with the required country code.

    Scenario: Country code is "+48", but input starts with "+1".
    We expect an error explicitly mentioning the required prefix.
    """
    v = Validator("+1123456789").is_phone(country_code="+48")
    assert v.is_valid() is False
    assert any("must start with +48" in e for e in v.get_errors())


def test_is_phone_with_specific_code_fail_digits():
    """
    Tests strict format validation: correct prefix but invalid characters.

    Scenario: Prefix is correct (+380), but the body contains letters ("testtest").
    This ensures the regex checks the ENTIRE string, not just the prefix.
    """
    v = Validator("+380testtest").is_phone(country_code="+380")
    assert v.is_valid() is False
    # The error might be about format or prefix, checking for the prefix mention is safe
    assert any("must start with +380" in e for e in v.get_errors())


def test_is_phone_generic_pass():
    """
    Tests .is_phone() in generic mode (no country code specified).

    Scenario: A valid E.164-like number (plus sign followed by digits).
    Should pass regardless of the specific country prefix.
    """
    v = Validator("+1234567890123").is_phone()
    assert v.is_valid() is True


def test_is_phone_generic_fail_no_plus():
    """
    Tests .is_phone() generic mode failure.

    Scenario: Number is missing the leading '+' sign.
    This verifies the regex requirement for the international format marker.
    """
    v = Validator("123456789").is_phone()
    assert v.is_valid() is False
    assert any("Invalid phone format" in e for e in v.get_errors())


def test_is_email_with_required_domain_pass():
    """
    Tests .is_email() with a required domain constraint (Success case).

    Scenario: Email domain exactly matches the required_domain argument.
    """
    v = Validator("user@mycompany.com").is_email(required_domain="mycompany.com")
    assert v.is_valid() is True


def test_is_email_with_required_domain_fail():
    """
    Tests .is_email() with a required domain constraint (Failure case).

    Scenario: Email is valid, but belongs to a different domain than required.
    We expect an error message specifying the required domain.
    """
    v = Validator("user@other.com").is_email(required_domain="mycompany.com")
    assert v.is_valid() is False
    assert any("must be from domain @mycompany.com" in e for e in v.get_errors())


def test_is_email_with_required_domain_case_insensitive():
    """
    Tests that domain validation is case-insensitive.

    Scenario 1: Input email has uppercase domain.
    Scenario 2: Required domain argument is uppercase.
    Both should match correctly because domains are case-insensitive in reality.
    """
    v = Validator("user@MYCOMPANY.COM").is_email(required_domain="mycompany.com")
    assert v.is_valid() is True

    v2 = Validator("user@mycompany.com").is_email(required_domain="MYCOMPANY.COM")
    assert v2.is_valid() is True


def test_is_email_required_domain_but_invalid_format():
    """
    Tests priority of checks in .is_email().

    Scenario: Input is not even a valid email format (missing @ or domain).
    The validator should report "Invalid email format" and NOT try to check the domain
    (which would cause a crash or logic error if parsing failed).
    """
    v = Validator("usermycompany.com").is_email(required_domain="mycompany.com")
    assert v.is_valid() is False
    assert len(v.get_errors()) == 1
    assert any("Invalid email format" in e for e in v.get_errors())