import re
import numbers

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)
class Validator:
    def __init__(self, value):
        self.value = value
        self.errors = []
        self._stop_validation = False
        
        if self.value is None:
            self._add_error("Value cannot be None")
            self._stop_validation = True

    def _add_error(self, message: str):
        """Допоміжний метод для додавання помилки."""
        self.errors.append(message)

    def is_valid(self) -> bool:
        """Повертає True, якщо не було зібрано жодної помилки."""
        return len(self.errors) == 0

    def get_errors(self) -> list[str]:
        """Повертає список усіх зібраних помилок."""
        return self.errors

    def is_type(self, expected_type: type, message: str | None = None):
        """Перевіряє, чи значення має очікуваний тип."""
        if self._stop_validation:
            return self
            
        if not isinstance(self.value, expected_type):
            self._add_error(message or f"Value must be of type {expected_type.__name__}, got {type(self.value).__name__}")
            self._stop_validation = True
        return self

    def is_not_empty(self, message: str | None = None):
        """Перевіряє, що рядок не порожній і не складається з пробілів."""
        self.is_type(str)
        if self._stop_validation:
            return self

        if not self.value.strip():
            self._add_error(message or "Value cannot be empty or whitespace")
        return self

    def is_in_range(self, min_val: numbers.Number, max_val: numbers.Number, message: str | None = None):
        """Перевіряє, що число знаходиться в діапазоні [min, max]."""
        self.is_type(numbers.Number)
        if self._stop_validation:
            return self
        
        if not (min_val <= self.value <= max_val):
            self._add_error(message or f"Value must be between {min_val} and {max_val}")
        return self

    def is_email(self, required_domain: str | None = None, message: str | None = None):
        """
        Перевіряє, чи рядок є валідним email.
        Якщо 'required_domain' вказано, перевіряє, що email
        належить саме цьому домену.
        """
        self.is_type(str)
        if self._stop_validation:
            return self

        # 1. Загальна перевірка формату
        if not EMAIL_REGEX.match(self.value):
            self._add_error(message or "Invalid email format")
            return self  # Провалено, виходимо
        
        # 2. Якщо формат коректний, перевіряємо домен
        if required_domain:
            try:
                domain = self.value.split('@', 1)[1]
                
                if domain.lower() != required_domain.lower():
                    self._add_error(message or f"Email must be from domain @{required_domain}")
            except IndexError:
                self._add_error(message or "Invalid email format, cannot check domain")
                
        return self

    def is_strong_password(self, min_len: int = 8, message: str | None = None):
        """Перевіряє пароль на складність."""
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
        """Перевіряє рядок за кастомним regex."""
        self.is_type(str)
        if self._stop_validation:
            return self
        
        if not re.match(pattern, self.value):
            self._add_error(message or f"Value does not match pattern '{pattern}'")
        return self

    def is_phone(self, country_code: str | None = None, message: str | None = None):
        """
        Перевіряє номер телефону.
        Якщо 'country_code' вказано (напр., '+380'), перевіряє точний префікс.
        Якщо ні, перевіряє загальний E.164-подібний формат (просто '+' і цифри).
        """
        if country_code:
            pattern = re.compile(r'^{}\d+$'.format(re.escape(country_code)))
            default_message = message or f"Phone must start with {country_code} and be followed by digits"
        else:
            # Загальний E.164-подібний формат (плюс і одна або більше цифр)
            pattern = re.compile(r'^\+\d+$')
            default_message = message or "Invalid phone format, expected +[code][number]"
        
        return self.matches_regex(pattern, default_message)
