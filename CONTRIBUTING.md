# Contributing to OmniCard-AI

Thank you for your interest in contributing to OmniCard-AI! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

### Suggesting Enhancements

For feature requests or enhancements:
- Use a clear, descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- Include any relevant examples or mockups

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Open a Pull Request

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install development dependencies: `pip install -r requirements-dev.txt` (if available)

## Coding Standards

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused on a single task
- Write tests for new features

## Testing

- Run tests before submitting a PR: `pytest`
- Ensure all tests pass
- Add new tests for new features

## Documentation

- Update documentation for any changes to the API or functionality
- Use clear, concise language
- Include examples where appropriate

## License

By contributing to OmniCard-AI, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). 