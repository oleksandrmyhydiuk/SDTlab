"""!
@file validator_v2.py
@brief Advanced validator class with support for method chaining,
error collection, custom phone codes, and email domains.
"""

import re
import numbers

# Compiled regex for email
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


class Validator:
    """!
    @brief Main class for performing validation on a single value.

    The validator is stateful. It collects errors in an internal list
    and supports method chaining.

    @example
    >>> v = Validator(10).is_in_range(0, 20)
    >>> v.is_valid()
    True

    >>> v2 = Validator("").is_not_empty().is_email()
    >>> v2.is_valid()
    False
    >>> v2.get_errors()
    ['Value cannot be empty or whitespace']
    """

    def __init__(self, value):
        """!
        @brief Initializes the Validator with a value to check.

        @param value (any): The value to be validated.
        """
        self.value = value
        self.errors = []
        # Flag to avoid checking None or wrong type
        # in every method if it has already failed.
        self._stop_validation = False

        if self.value is None:
            self._add_error("Value cannot be None")
            self._stop_validation = True

    def _add_error(self, message: str):
        """!
        @brief Private helper method to add an error to the internal list.

        @param message (str): The error message to add.
        """
        self.errors.append(message)

    def is_valid(self) -> bool:
        """!
        @brief Checks if the validation has passed.

        @return bool: True if no errors were collected, False otherwise.
        """
        return len(self.errors) == 0

    def get_errors(self) -> list[str]:
        """!
        @brief Retrieves the list of collected error messages.

        @return list[str]: A list of all error messages.
        """
        return self.errors

    def is_type(self, expected_type: type, message: str | None = None):
        """!
        @brief Checks if the value is of the expected type.

        If the type is wrong, this sets a flag to stop further
        validations to prevent TypeErrors.

        @param expected_type (type): The type to check against (e.g., str, int).
        @param message (str, optional): Custom error message.

        @return Validator: self, for method chaining.
        """
        if self._stop_validation:
            return self

        if not isinstance(self.value, expected_type):
            self._add_error(
                message or f"Value must be of type {expected_type.__name__}, got {type(self.value).__name__}")
            self._stop_validation = True
        return self

    def is_not_empty(self, message: str | None = None):
        """!
        @brief Checks that a string is not empty or just whitespace.
        Automatically performs an is_type(str) check first.

        @param message (str, optional): Custom error message.

        @return Validator: self, for method chaining.
        """
        self.is_type(str)
        if self._stop_validation:
            return self

        if not self.value.strip():
            self._add_error(message or "Value cannot be empty or whitespace")
        return self

    def is_in_range(self, min_val: numbers.Number, max_val: numbers.Number, message: str | None = None):
        """!
        @brief Checks that a number is within a specific range (inclusive).
        Automatically performs an is_type(numbers.Number) check first.

        @param min_val (numbers.Number): The minimum allowed value.
        @param max_val (numbers.Number): The maximum allowed value.
        @param message (str, optional): Custom error message.

        @return Validator: self, for method chaining.
        """
        self.is_type(numbers.Number)
        if self._stop_validation:
            return self

        if not (min_val <= self.value <= max_val):
            self._add_error(message or f"Value must be between {min_val} and {max_val}")
        return self

    def is_email(self, required_domain: str | None = None, message: str | None = None):
        """!
        @brief Checks if the string is a valid email.

        If 'required_domain' is provided, it also checks if the email
        belongs to that specific domain (case-insensitive).

        @param required_domain (str, optional): The domain the email must belong to.
        @param message (str, optional): Custom error message. This will override
                both format and domain error messages.

        @return Validator: self, for method chaining.
        """
        self.is_type(str)
        if self._stop_validation:
            return self

        if not EMAIL_REGEX.match(self.value):
            self._add_error(message or "Invalid email format")
            return self

        if required_domain:
            try:
                domain = self.value.split('@', 1)[1]
                if domain.lower() != required_domain.lower():
                    self._add_error(message or f"Email must be from domain @{required_domain}")
            except IndexError:
                self._add_error(message or "Invalid email format, cannot check domain")

        return self

    def is_strong_password(self, min_len: int = 8, message: str | None = None):
        """!
        @brief Checks password complexity based on multiple criteria.

        Criteria:
        - At least `min_len` characters.
        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one digit.
        - At least one special symbol (@$!%*?&#).

        @param min_len (int, optional): The minimum password length. Defaults to 8.
        @param message (str, optional): Custom error message prefix.

        @return Validator: self, for method chaining.
        """
        self.is_type(str)
        if self._stop_validation:
            return self

        errors = []
        if len(self.value) < min_len:
            errors.append(f"must be at least {min_len} characters")
        if not re.search(r'[A-Z]', self.value):
            errors.append("must contain one uppercase letter")
        if not re.search(r'[a-z]', self.value):
            errors.append("must contain one lowercase letter")
        if not re.search(r'\d', self.value):
            errors.append("must contain one digit")
        if not re.search(r'[@$!%*?&#]', self.value):
            errors.append("must contain one special symbol")

        if errors:
            full_message = (message or "Password is not strong") + ": " + ", ".join(errors)
            self._add_error(full_message)
        return self

    def matches_regex(self, pattern: str | re.Pattern, message: str | None = None):
        """!
        @brief Checks the string against a custom regex pattern.

        @param pattern (str | re.Pattern): The regex pattern to match.
        @param message (str, optional): Custom error message.

        @return Validator: self, for method chaining.
        """
        self.is_type(str)
        if self._stop_validation:
            return self

        if not re.match(pattern, self.value):
            self._add_error(message or f"Value does not match pattern '{pattern}'")
        return self

    def is_phone(self, country_code: str | None = None, message: str | None = None):
        """!
        @brief Checks a phone number.

        If 'country_code' is set (e.g., '+380'), it enforces that prefix.
        If not, it checks for a generic E.164-like format (+...digits...).

        @param country_code (str, optional): The specific country code prefix to enforce.
        @param message (str, optional): Custom error message.

        @return Validator: self, for method chaining.
        """
        if country_code:
            pattern = re.compile(r'^{}\d+\Z'.format(re.escape(country_code)))
            default_message = message or f"Phone must start with {country_code} and be followed by digits"
        else:
            pattern = re.compile(r'^\+\d+\Z')
            default_message = message or "Invalid phone format, expected +[code][number]"

        return self.matches_regex(pattern, default_message)