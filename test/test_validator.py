"""
@file test_validator.py
@brief Unit tests for the Validator class using pytest.

This test suite validates the Validator class functionality using pytest.
It incorporates robust checking (using 'any' and 'in' instead of exact matching)
and avoids fragile asserts, as per code review feedback.
It uses @pytest.mark.parametrize to efficiently test multiple scenarios.
"""

import pytest
from validator import Validator


# --- 1. Base Logic and Chaining Tests ---

def test_valid_chain_email():
    """Test a successful validation chain for a valid email."""
    v = Validator("test@example.com").is_not_empty().is_email()
    assert v.is_valid() is True
    assert v.get_errors() == []


def test_valid_chain_number():
    """Test a successful validation chain for a valid number in range."""
    v = Validator(10).is_in_range(5, 15)
    assert v.is_valid() is True
    assert v.get_errors() == []


def test_chain_fail_at_first_step():
    """Test a chain that correctly fails on the first validation step."""
    v = Validator("  ").is_not_empty().is_email()
    assert v.is_valid() is False
    assert any("Value cannot be empty" in e for e in v.get_errors())


def test_chain_fail_at_second_step():
    """Test a chain that correctly fails on the second validation step."""
    v = Validator("not-an-email").is_not_empty().is_email()
    assert v.is_valid() is False
    assert any("Invalid email format" in e for e in v.get_errors())


def test_chain_multiple_errors():
    """Test that the chain collects multiple errors from different checks."""
    v = Validator("not-an-email").is_email().is_strong_password()
    assert v.is_valid() is False
    assert len(v.get_errors()) >= 2
    assert any("Invalid email format" in e for e in v.get_errors())
    assert any("Password is not strong" in e for e in v.get_errors())


def test_stop_validation_on_type_error():
    """Test that validation stops after a critical type error."""
    v = Validator(12345).is_not_empty().is_email()
    assert v.is_valid() is False
    # Check that ONLY the type error is logged
    assert len(v.get_errors()) == 1
    assert any("Value must be of type str" in e for e in v.get_errors())


def test_none_input():
    """Test that the validator correctly handles None as input."""
    v = Validator(None)
    assert v.is_valid() is False
    assert len(v.get_errors()) == 1
    assert any("Value cannot be None" in e for e in v.get_errors())

    # Check that subsequent calls do not add more errors
    v.is_email().is_not_empty()
    assert len(v.get_errors()) == 1, "Further validations should not add more errors"


# --- 2. Parametrized Tests for Individual Methods ---

@pytest.mark.parametrize("value, expected_valid", [
    (10, True),  # In range
    (0, True),  # At min boundary
    (100, True),  # At max boundary
    (-1, False),  # Below min
    (101, False),  # Above max
])
def test_is_in_range(value, expected_valid):
    """
    Parametrized test for the is_in_range method.

    @param value The value to test.
    @param expected_valid The expected validation outcome (True/False).
    """
    v = Validator(value).is_in_range(0, 100)
    assert v.is_valid() is expected_valid
    if not expected_valid:
        assert any("must be between 0 and 100" in e for e in v.get_errors())


@pytest.mark.parametrize("password, expected_valid, contains_error", [
    ("P@ssword123", True, None),  # Valid
    ("P@s1", False, "at least 8 characters"),  # Too short
    ("p@ssword123", False, "one uppercase letter"),  # No uppercase
    ("P@SSWORD123", False, "one lowercase letter"),  # No lowercase
    ("P@sswordABC", False, "one digit"),  # No digit
    ("Password123", False, "one special symbol"),  # No special char
    ("weak", False, "at least 8 characters"),  # Multiple failures
])
def test_is_strong_password(password, expected_valid, contains_error):
    """
    Parametrized test for the is_strong_password method.

    @param password The password string to test.
    @param expected_valid The expected validation outcome (True/False).
    @param contains_error A substring expected in the error message if invalid.
    """
    v = Validator(password).is_strong_password()
    assert v.is_valid() is expected_valid
    if not expected_valid:
        assert len(v.get_errors()) > 0
        assert any(contains_error in e for e in v.get_errors())


def test_password_multiple_failings():
    """Test password that fails multiple checks simultaneously."""
    v = Validator("weak").is_strong_password()
    assert v.is_valid() is False
    errors = v.get_errors()
    assert len(errors) > 0
    combined_errors = " ".join(errors)

    assert "at least 8 characters" in combined_errors
    assert "one uppercase letter" in combined_errors
    assert "one digit" in combined_errors
    assert "one special symbol" in combined_errors


# --- 3. Custom Message Tests ---

def test_custom_error_message_is_not_empty():
    """Test that a custom error message is used and checked exactly."""
    custom_msg = "Email є обов'язковим полем"
    v = Validator("").is_not_empty(message=custom_msg)
    assert v.is_valid() is False
    assert v.get_errors() == [custom_msg]


def test_custom_error_message_is_phone():
    """Test that a custom error message is used for the phone check."""
    custom_msg = "Введіть коректний номер +380"
    v = Validator("12345").is_phone(country_code="+380", message=custom_msg)
    assert v.is_valid() is False
    assert v.get_errors() == [custom_msg]


def test_custom_error_message_is_email_domain():
    """Test that a custom error message is used for the domain check."""
    custom_msg = "Дозволені лише корпоративні адреси"
    v = Validator("user@gmail.com").is_email(required_domain="corp.com", message=custom_msg)
    assert v.is_valid() is False
    assert v.get_errors() == [custom_msg]


# --- 4. New Feature Tests (Domains and Country Codes) ---

def test_is_phone_with_specific_country_code_pass():
    """Test: valid number with specified country code."""
    v = Validator("+48123456789").is_phone(country_code="+48")
    assert v.is_valid() is True


def test_is_phone_with_specific_country_code_fail():
    """Test: invalid number (different code)."""
    v = Validator("+1123456789").is_phone(country_code="+48")
    assert v.is_valid() is False
    assert any("must start with +48" in e for e in v.get_errors())


def test_is_phone_with_specific_code_fail_digits():
    """Test: code is correct, but followed by letters."""
    v = Validator("+380testtest").is_phone(country_code="+380")
    assert v.is_valid() is False
    assert any("must start with +380" in e for e in v.get_errors())


def test_is_phone_generic_pass():
    """Test: valid number (general format) without specified code."""
    v = Validator("+1234567890123").is_phone()
    assert v.is_valid() is True


def test_is_phone_generic_fail_no_plus():
    """Test: invalid number (general format) - no '+'."""
    v = Validator("123456789").is_phone()
    assert v.is_valid() is False
    assert any("Invalid phone format" in e for e in v.get_errors())


def test_is_email_with_required_domain_pass():
    """Test: valid email with correct domain."""
    v = Validator("user@mycompany.com").is_email(required_domain="mycompany.com")
    assert v.is_valid() is True


def test_is_email_with_required_domain_fail():
    """Test: valid email, but incorrect domain."""
    v = Validator("user@other.com").is_email(required_domain="mycompany.com")
    assert v.is_valid() is False
    assert any("must be from domain @mycompany.com" in e for e in v.get_errors())


def test_is_email_with_required_domain_case_insensitive():
    """Test: domain check is case-insensitive."""
    v = Validator("user@MYCOMPANY.COM").is_email(required_domain="mycompany.com")
    assert v.is_valid() is True

    v2 = Validator("user@mycompany.com").is_email(required_domain="MYCOMPANY.COM")
    assert v2.is_valid() is True


def test_is_email_required_domain_but_invalid_format():
    """Test: email is invalid, domain check should not trigger."""
    v = Validator("usermycompany.com").is_email(required_domain="mycompany.com")
    assert v.is_valid() is False
    # Check that there is ONE error, and it's about the format
    assert len(v.get_errors()) == 1
    assert any("Invalid email format" in e for e in v.get_errors())