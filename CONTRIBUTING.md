# Contributing

Thank you for your interest in contributing to **VideoQA Gate**!

## How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs or suggest features
- Include reproduction steps, expected vs actual behavior
- For video quality issues, include sample outputs if possible

### Pull Requests
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest tests/`
6. Submit a PR with a clear description

### Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/ai-short-video-research.git
cd ai-short-video-research
pip install -e ".[dev]"
```

### Code Style
- Follow PEP 8
- Use type hints
- Keep functions focused and well-documented
- Write tests for new quality check functions

### Areas We Need Help
- **New quality checks**: Additional Layer 1/2 checks
- **VLM prompt engineering**: Better evaluation prompts for Layer 3
- **Generator adapters**: Integrations with more video generation APIs
- **Benchmarks**: Test with diverse video samples and report results
- **Documentation**: Improve docs, add examples, translate

## Code of Conduct
Be respectful, constructive, and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).
