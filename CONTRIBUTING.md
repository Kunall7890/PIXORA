# 🤝 Contributing to Pixora

Thank you for your interest in contributing! This guide will help you get started.

## Code of Conduct

- Be respectful and inclusive
- Focus on the problem, not the person
- Be open to feedback
- Help others learn

## Getting Started

### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/yourusername/pixora.git
cd pixora
```

### 2. Create a Branch

```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Or bug fix branch
git checkout -b bugfix/issue-description
```

### 3. Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest black flake8 mypy
```

### 4. Make Changes

- Follow the code style (see below)
- Add tests for new features
- Update documentation
- Add comments for complex logic

### 5. Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov

# Run linters
black .
flake8 .
mypy .
```

### 6. Commit and Push

```bash
# Commit with clear message
git commit -m "Add: description of changes"

# Push to your fork
git push origin feature/amazing-feature
```

### 7. Create Pull Request

- Go to GitHub
- Create PR from your branch to main
- Write clear description
- Reference any related issues

## Code Style

### Python Style

We follow PEP 8 with some extensions:

```python
# Good
def calculate_quality_score(
    hallucination: float,
    consistency: float,
    branding: float
) -> float:
    """Calculate overall quality score."""
    return (hallucination + consistency + branding) / 3

# Bad
def calcQS(h, c, b):
    return (h+c+b)/3
```

### Naming Conventions

```python
# Variables
product_data = {}
GROQ_API_KEY = "..."

# Functions
def extract_product_info()
def generate_strategy()

# Classes
class ProductResearchAgent:
    pass

# Constants
HALLUCINATION_THRESHOLD = 0.7
MAX_BATCH_SIZE = 50
```

### Documentation

```python
def generate_prompts(self, product_data: Dict, creative_brief: Dict) -> Dict:
    """
    Generate optimized prompts for image and video generation.
    
    Args:
        product_data: Extracted product information
        creative_brief: Generated creative strategy
    
    Returns:
        Dict with image_prompts, video_scripts, visual_style_guide
    
    Raises:
        ValueError: If product_data is invalid
    
    Example:
        >>> prompts = agent.generate_prompts(data, brief)
        >>> len(prompts['image_prompts'])
        5
    """
```

## Adding New Features

### Add a New Agent

1. Create file: `agents/new_agent.py`
2. Implement agent class
3. Add to orchestration
4. Update API endpoints
5. Add tests
6. Update README

### Add API Endpoint

1. Edit `api/main.py`
2. Add Pydantic model in `api/models.py`
3. Add handler function
4. Add tests
5. Document in README

### Add UI Component

1. Edit `frontend/app.py`
2. Add Streamlit widgets
3. Test in browser
4. Update DOCUMENTATION.md

## Testing

### Write Tests

```python
# tests/test_research_agent.py
import pytest
from agents.research_agent import ProductResearchAgent

@pytest.mark.asyncio
async def test_extract_product_info():
    agent = ProductResearchAgent()
    result = await agent.extract_product_info("https://example.com")
    
    assert result["title"] is not None
    assert result["price"] is not None
    assert isinstance(result["features"], list)

@pytest.mark.asyncio
async def test_invalid_url():
    agent = ProductResearchAgent()
    result = await agent.extract_product_info("not-a-url")
    
    assert result["status"] == "error"
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_research_agent.py::test_extract_product_info

# Run with coverage
pytest --cov=agents --cov=api tests/
```

## Documentation

### Update README

- Add new features to feature list
- Update architecture diagram if needed
- Add usage examples
- Document breaking changes

### Update DOCUMENTATION.md

- Explain how new components work
- Add architecture diagram if applicable
- Document configuration options
- Add troubleshooting tips

### Add Docstrings

```python
# Module docstring
"""
Product Research Agent
Extracts and understands product information from URLs
"""

# Class docstring
class ProductResearchAgent:
    """Scrapes and extracts product data from e-commerce URLs."""

# Function docstring
def extract_product_info(self, url: str) -> Dict:
    """
    Extract product information from URL.
    
    Args:
        url: E-commerce product URL
    
    Returns:
        Dict with product data
    """
```

## Performance Considerations

- Use async/await for I/O operations
- Cache expensive operations
- Optimize database queries
- Monitor memory usage
- Test with realistic data

## Security

- Never commit API keys
- Validate all user inputs
- Use HTTPS for external APIs
- Sanitize file paths
- Add rate limiting
- Use security headers

## Common Issues

### ImportError: No module named 'fastapi'

```bash
# Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### Tests failing

```bash
# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_file.py::test_function
```

### Code style issues

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

## Release Process

1. Update version in `config.py`
2. Update CHANGELOG.md
3. Update README with new features
4. Create release branch: `release/v1.x.x`
5. Create GitHub release
6. Merge to main

## Communication

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: support@pixora.dev (for security issues)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md
- README.md
- GitHub Contributors page

## Questions?

- Check existing issues/discussions
- Read DOCUMENTATION.md
- Ask in Discord community
- Email: support@pixora.dev

## Thank You!

Your contributions make Pixora better for everyone. 🙏

---

Happy contributing! 🚀
