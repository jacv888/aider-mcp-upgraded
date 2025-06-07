# Contributing to Aider-MCP

Thank you for your interest in contributing to Aider-MCP! We welcome contributions from the community to help make this AI coding server even better.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- API keys for AI models (OpenAI, Anthropic, Google)

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/jacv888/aider-mcp-upgraded.git
cd aider-mcp-upgraded

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Install resilience features
python3 install_resilience.py --install

# Run tests to verify setup
python tests/test_multiple_ai.py
```

## 🛠️ Development Guidelines

### Code Quality
- Follow PEP 8 Python style guidelines
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Write comprehensive tests for new features

### Testing
- Test both single and multiple AI operations
- Verify resilience features remain active
- Check strategic model selection accuracy
- Validate configuration priority system

### Resilience Testing
```bash
# Test resilience features
python tests/multi-ai-2/resilience-test.py

# Run comprehensive test suite
python -m pytest tests/
```

## 🎯 Areas for Contribution

### High Priority
- 🧠 **Strategic Model Selection**: Improve model selection algorithms
- 🛡️ **Resilience Features**: Add new stability patterns
- ⚙️ **Configuration**: Extend configuration options
- 📊 **Monitoring**: Enhance performance metrics

### Medium Priority
- 📚 **Documentation**: Improve guides and examples
- 🧪 **Testing**: Add more comprehensive test cases
- 🔧 **Tools**: Build development and deployment tools
- 🎨 **UI/UX**: Improve user experience

### Good First Issues
- 📝 Fix typos in documentation
- 🐛 Add error handling for edge cases
- ✨ Add new model configurations
- 🔧 Improve installation scripts

## 📋 Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Implement** your changes with tests
4. **Test** thoroughly:
   ```bash
   # Test resilience
   python tests/multi-ai-2/resilience-test.py
   
   # Test functionality
   python tests/test_multiple_ai.py
   ```
5. **Commit** with clear messages
6. **Push** to your fork
7. **Submit** a pull request

### Pull Request Guidelines
- Clear description of changes
- Link to related issues
- Include test results
- Update documentation if needed
- Ensure CI passes

## 🐛 Bug Reports

When reporting bugs, include:
- Python version
- OS and version
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs
- Configuration details (without API keys)

## 💡 Feature Requests

For new features, include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Impact on existing functionality

## 🔐 Security

For security issues:
- **Do not** create public issues
- Email: security@jacv888.dev
- Include detailed description
- Provide reproduction steps if safe

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes
- Contributors page

## 📞 Questions?

- 💬 **Discussions**: GitHub Discussions for questions
- 🐛 **Issues**: GitHub Issues for bugs and features
- 📧 **Email**: contribute@jacv888.dev for other inquiries

---

**Thank you for helping make Aider-MCP better! 🚀**
