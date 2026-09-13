# Changelog

## [v0.1.0-alpha] - 2026-09-13

### 🎉 Initial Release - German Language Learning AI Agent

**This is the alpha release of Lernen-Deutsch, a CLI-based interactive German language learning platform powered by OpenAI's language models.**

### ✨ Features

#### Core Functionality
- 🤖 **Intelligent Tutoring Agent**: Interactive German language learning through conversational AI
- 💬 **Real-time Chat Interface**: Engage in German conversations with immediate feedback
- ✍️ **Grammar Correction**: Automatic detection and explanation of grammar mistakes
- 🎓 **Educational Context**: Native speaker pronunciation and cultural explanations
- 🌐 **Multi-language Explanations**: Corrections explained in English or Chinese for clarity

#### Development & DevOps
- 🔄 **GitHub Actions CI/CD**: Automated testing pipeline
- 📊 **Code Coverage**: pytest + codecov integration
- 🔍 **Code Quality**: Black, Flake8, MyPy linting and type checking
- 🔒 **Security Scanning**: Bandit and detect-secrets security analysis
- 🪝 **Pre-commit Hooks**: Enforce code standards before commits
- 📝 **Contribution Guidelines**: Comprehensive CONTRIBUTING.md

### 📦 Project Structure

```
Lernen-Deutsch/
├── main.py                        # CLI tutoring agent entry point
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── CONTRIBUTING.md                # Contribution guidelines
├── pytest.ini                     # Pytest configuration
├── .pre-commit-config.yaml        # Pre-commit hooks setup
├── .github/
│   └── workflows/
│       └── tests.yml              # GitHub Actions CI/CD pipeline
└── tests/
    ├── __init__.py
    └── test_main.py               # Unit tests
```

### 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/whs2020944651-eng/Lernen-Deutsch.git
cd Lernen-Deutsch

# Setup environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key-here"

# Run tutoring agent
python main.py
```

### 🧪 Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=. --cov-report=html

# Check code quality
black . --check
flake8 .
mypy main.py --ignore-missing-imports
```

### 📋 Roadmap

Active development on the following features:

- **#1** Feature: Add SQLite Database for Vocabulary Management
- **#2** Docs: Write Comprehensive Usage Guide and API Documentation
- **#3** Enhancement: Expand CI/CD Pipeline with Code Coverage and Security Scanning
- **#4** Feature: Support Voice Input/Output via OpenAI Whisper & TTS

### 🔧 System Requirements

- Python 3.9+
- OpenAI API Key (for GPT models)
- pip package manager

### 📚 Dependencies

**Production**:
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management

**Development**:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker
- `bandit` - Security scanner
- `detect-secrets` - Secret detection
- `pre-commit` - Git hooks manager

### 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines:

- Code style: PEP 8 with Black formatter
- Minimum test coverage: 80%
- All CI checks must pass
- PRs must link to related issues

### 📝 License

This project is open source. See LICENSE file for details.

### 🙏 Acknowledgments

- OpenAI for GPT API and Whisper speech-to-text
- Python community for excellent testing tools
- Contributors and early testers

### 📧 Support

For issues, feature requests, or questions:
- Open an [Issue](https://github.com/whs2020944651-eng/Lernen-Deutsch/issues)
- Start a [Discussion](https://github.com/whs2020944651-eng/Lernen-Deutsch/discussions)

---

**Want to help?** Check our [open issues](https://github.com/whs2020944651-eng/Lernen-Deutsch/issues) 
and [CONTRIBUTING.md](CONTRIBUTING.md) to get started! 🚀
