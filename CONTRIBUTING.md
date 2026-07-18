# Contributing to BYOD Compliance Monitor

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/byod-compliance-monitor.git`
3. Create virtual environment: `python -m venv venv && source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create branch: `git checkout -b feature/your-feature`

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for all classes and methods
- Keep functions small and focused
- Add error handling for all external operations

## Testing

- Write tests for new features
- Ensure all existing tests pass
- Test with different Android versions when possible

## Pull Request Process

1. Update documentation for any changes
2. Add entry to CHANGELOG.md
3. Ensure all tests pass
4. Request review from maintainers
5. Squash commits before merging

## Security

- Never commit credentials or sensitive data
- Report security issues privately
- Follow responsible disclosure practices
