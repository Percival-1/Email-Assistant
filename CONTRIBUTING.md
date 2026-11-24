# Contributing to AI Email Assistant

Thank you for considering contributing to this project! Here's how you can help.

## 🤝 Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit bug fixes
- ✨ Add new features

## 🔧 Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/agents-from-scratch.git
   cd agents-from-scratch
   ```

2. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up pre-commit hooks** (optional)
   ```bash
   pre-commit install
   ```

## 📋 Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep functions focused and small

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

```bash
pytest tests/
pytest tests/ --cov=src/email_assistant
```

### Documentation

- Update README.md if adding new features
- Add docstrings to new functions
- Update relevant .md guides in root directory

## 🔄 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests**
   ```bash
   pytest tests/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Describe what changes you made
   - Reference any related issues
   - Add screenshots if applicable

## 🐛 Reporting Bugs

When reporting bugs, please include:

- Python version
- OS and version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs

## 💡 Suggesting Features

Feature requests are welcome! Please:

- Check if it's already been requested
- Explain the use case
- Describe the proposed solution
- Consider alternatives

## 📞 Questions?

- Open a [Discussion](https://github.com/yourusername/agents-from-scratch/discussions)
- Create an [Issue](https://github.com/yourusername/agents-from-scratch/issues)

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

Thank you for contributing! 🎉
