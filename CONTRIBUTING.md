# Contributing to BookStore API

We love your input! We want to make contributing to BookStore API as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

### Quick Start
```bash
# Clone your fork
git clone https://github.com/your-username/bookstore-api.git
cd bookstore-api

# Setup development environment
./scripts/setup-dev.sh

# Start development server
make dev
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

# Setup environment
cp .env.example .env

# Run tests
make test

# Start development server
make dev
```

## Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all checks:
```bash
make lint
```

Auto-format code:
```bash
make format
```

## Testing

We maintain high test coverage and use multiple testing strategies:

### Running Tests
```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-property
make test-performance

# Run with coverage
make test-coverage
```

### Writing Tests

1. **Unit Tests**: Test individual functions and classes
   - Location: `tests/test_unit_*.py`
   - Use pytest fixtures from `tests/conftest.py`

2. **Integration Tests**: Test API endpoints
   - Location: `tests/test_api_*.py`
   - Use the test client from `tests/conftest.py`

3. **Property-Based Tests**: Test with generated data
   - Location: `tests/test_property_*.py`
   - Use Hypothesis for property-based testing

4. **Performance Tests**: Test system performance
   - Location: `tests/test_performance.py`
   - Use Locust for load testing

### Test Guidelines

- Write descriptive test names
- Use fixtures for common setup
- Test both success and error cases
- Aim for high coverage but focus on meaningful tests
- Use property-based testing for complex logic

## Documentation

### API Documentation
- API docs are auto-generated from code
- Add docstrings to all public functions
- Use type hints consistently

### User Documentation
- Update README.md for user-facing changes
- Add examples to `examples/` directory
- Update deployment guides in `docs/`

## Security

### Reporting Security Issues

Please do not report security vulnerabilities through public GitHub issues. Instead, send an email to security@bookstore-api.com.

### Security Guidelines

- Never commit secrets or credentials
- Use environment variables for configuration
- Follow OWASP security guidelines
- Run security scans: `make security-scan`

## Performance

### Performance Guidelines

- Use async/await for I/O operations
- Implement proper caching strategies
- Monitor database query performance
- Run performance tests: `make load-test`

### Benchmarking

- Use the included Locust configuration
- Test against realistic data volumes
- Monitor response times and throughput
- Check resource usage (CPU, memory)

## Docker and Deployment

### Local Development
```bash
# Start with Docker
make docker-dev

# Check logs
make logs

# Stop services
docker-compose down
```

### Testing Deployment
```bash
# Test production build
docker build -t bookstore-api:test .

# Test Kubernetes deployment
make k8s-deploy
```

## Issue and Bug Reports

We use GitHub issues to track public bugs. Report a bug by opening a new issue.

### Bug Report Template

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.11]
- Docker version: [e.g. 24.0.0]

**Additional context**
Add any other context about the problem here.

## Feature Requests

We welcome feature requests! Please provide:

1. **Use case**: Why do you need this feature?
2. **Proposed solution**: How should it work?
3. **Alternatives**: What alternatives have you considered?
4. **Additional context**: Any other relevant information

## Code Review Process

### For Contributors

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Update documentation
5. Run the full test suite
6. Submit a pull request

### For Maintainers

1. Review code for correctness and style
2. Check that tests are adequate
3. Verify documentation is updated
4. Run CI/CD pipeline
5. Merge when approved

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality
- PATCH version for backwards-compatible bug fixes

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Create release tag
5. Deploy to staging
6. Run smoke tests
7. Deploy to production
8. Monitor for issues

## Community

### Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code.

### Getting Help

- Check the documentation first
- Search existing issues
- Ask questions in discussions
- Join our community chat

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Don't hesitate to ask! You can:
- Open an issue for bugs or feature requests
- Start a discussion for questions
- Contact maintainers directly

Thank you for contributing to BookStore API! 🚀