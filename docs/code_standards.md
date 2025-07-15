# Code Standards

This project adheres to the following Python code standards:

## PEP 8

All Python code should follow the [PEP 8 style guide](https://www.python.org/dev/peps/pep-0008/). Key aspects include:

*   **Indentation:** Use 4 spaces per indentation level.
*   **Line Length:** Limit all lines to a maximum of 79 characters.
*   **Blank Lines:** Use blank lines to separate logical sections of code.
*   **Imports:** Imports should be on separate lines and grouped as follows:
    1.  Standard library imports.
    2.  Third-party imports.
    3.  Local application/library specific imports.

    Each group should be separated by a blank line.

*   **Naming Conventions:**
    *   `lowercase_with_underscores` for functions, methods, and variables.
    *   `CapitalizedWords` for class names.
    *   `UPPERCASE_WITH_UNDERSCORES` for constants.

## Docstrings

All modules, functions, classes, and methods should have docstrings that explain their purpose, arguments, and return values. We follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#pyguide-python-style-rules) for docstrings.

## Type Hinting

Use type hints for function arguments and return values to improve code readability and maintainability. This helps with static analysis and makes the code easier to understand.

## Error Handling

Use `try-except` blocks for handling expected errors gracefully. Avoid broad `except` clauses; catch specific exceptions whenever possible.

## Logging

Use Python's built-in `logging` module for logging events. Avoid `print()` statements for debugging or informational output in production code.
