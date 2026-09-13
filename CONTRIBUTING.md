# Contributing to Lernen-Deutsch 🇩🇪

Thank you for your interest in contributing to **Lernen-Deutsch**! We welcome contributions from everyone. This guide will help you get started.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git
- OpenAI API Key (for development and testing)

### Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/whs2020944651-eng/Lernen-Deutsch.git
   cd Lernen-Deutsch
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Create a `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## 📝 Code Style Guidelines

We follow **PEP 8** with the following tools:

- **Black**: Code formatting (100 character line length)
- **Flake8**: Linting
- **MyPy**: Type checking

### Running Code Quality Checks

```bash
# Format code with Black
black .

# Check with Flake8
flake8 .

# Type checking with MyPy
mypy main.py --ignore-missing-imports
```

### Pre-commit Hooks

All checks run automatically before commit. To run them manually:
```bash
pre-commit run --all-files
```

## 🧪 Testing

We use **pytest** for unit and integration testing.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_main.py -v
```

### Writing Tests

- Create test files in `tests/` directory with `test_*.py` naming
- Use descriptive test names: `test_<function>_<scenario>`
- Add docstrings to test functions
- Use pytest fixtures for setup/teardown

Example:
```python
def test_api_key_loading():
    """Test that API key is properly loaded"""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
        assert os.getenv("OPENAI_API_KEY") == "test"
```

## 📋 Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit:
   ```bash
   git commit -m "type: description

   - Detailed explanation of changes
   - Additional context if needed"
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request:**
   - Link to related Issues using `Resolves #<issue-number>`
   - Provide clear description of changes
   - Ensure all CI checks pass (tests, linting, coverage)
   - Minimum 80% code coverage required

5. **Code Review:**
   - Respond to reviewer feedback
   - Make requested changes in new commits
   - Re-request review after updates

## 🐛 Bug Reports

File issues with:
- **Clear title** describing the bug
- **Steps to reproduce**
- **Expected behavior** vs. **actual behavior**
- **Environment** (Python version, OS, etc.)
- **Error messages** or stack traces

## 💡 Feature Requests

Propose new features with:
- **Problem statement**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternative approaches**: Other options considered
- **Use cases**: Real-world examples

## 🔒 Security

- **Never commit API keys or secrets**
- Use `.env` files for sensitive data
- Report security vulnerabilities privately to maintainers

## 📚 Project Roadmap

Current priority features:
- [x] Basic CLI tutoring agent
- [ ] #1: SQLite database for vocabulary management
- [ ] #3: Enhanced CI/CD pipeline with code coverage
- [ ] #4: Voice input/output via Whisper & TTS
- [ ] #2: Comprehensive usage documentation

## ❓ Questions?

- Check existing Issues and Discussions
- Read the main README.md
- Open a Discussion for general questions

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for making Lernen-Deutsch better! 🎉
