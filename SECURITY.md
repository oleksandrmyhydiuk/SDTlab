# Security Policy

## Supported Versions

The following versions of **Python Validator (`SDTlab`)** are currently supported with security updates:

| Version / Branch | Supported          |
| ---------------- | ------------------ |
| `main` (latest)  | :white_check_mark: |
| `< 1.0`          | :x:                |

## Security Design Principles

This library validates untrusted user input and enforces several defensive programming practices:

1. **Strict Type Validation & Short-Circuiting:** Calling validation methods on `None` or incompatible types (including rejecting `bool` where numeric values are expected) immediately halts further rule evaluation (`_stop_validation = True`) to prevent unexpected runtime exceptions (`TypeError`, `AttributeError`).
2. **Strict End-of-String Regex Anchors (`\Z`):** Phone and pattern validations use `\Z` instead of `$` where appropriate so trailing newline characters (`\n`) cannot bypass validation checks.
3. **Safe Regular Expressions:** Built-in regular expressions (`EMAIL_REGEX`, phone format patterns, and character-class checks in `is_strong_password`) avoid nested quantifiers to mitigate Regular Expression Denial of Service (ReDoS) risks.
4. **Caution with Custom Regexes:** When using `.matches_regex(pattern)`, callers should avoid passing untrusted or user-supplied regular expressions without prior complexity verification.

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do not open a public GitHub issue** for security vulnerabilities.
2. Report the issue privately via [GitHub Security Advisories](https://github.com/oleksandrmyhydiuk/SDTlab/security/advisories/new) or by contacting the maintainer directly via GitHub ([@oleksandrmyhydiuk](https://github.com/oleksandrmyhydiuk)).
3. Include a clear description of the issue, steps to reproduce, and a minimal proof-of-concept input demonstrating the vulnerability.

### Response Timeline

- **Initial Acknowledgment:** Within 48 hours of receiving the report.
- **Triage & Assessment:** Within 5 business days.
- **Resolution & Patch Release:** Depending on severity, a fix will be prepared and merged into `main` as quickly as possible.
