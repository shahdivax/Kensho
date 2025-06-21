# 🤝 Contributing to Kensho

Thank you for your interest in contributing to Kensho! We welcome contributions from everyone and are grateful for every contribution.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome newcomers and help them succeed
- **Be collaborative**: Work together towards common goals
- **Be patient**: Remember that everyone has different experience levels
- **Be constructive**: Focus on what is best for the community

## 🚀 Getting Started

### Prerequisites

Before contributing, make sure you have:

- **Python 3.10+** installed
- **Node.js 18+** installed
- **Git** installed
- **FFmpeg** installed (for audio/video processing)
- API keys for **Gemini** and **Groq**

### First-time Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Kensho.git
   cd Kensho
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/shahdivax/Kensho.git
   ```
4. **Install dependencies**:
   ```bash
   # Backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   cd ..
   ```
5. **Set up environment**:
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys
   ```

## 🛠️ Development Setup

### Running the Development Environment

1. **Start the backend**:
   ```bash
   source venv/bin/activate  # Windows: venv\Scripts\activate
   python start_api.py
   ```

2. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Tools

We recommend using:

- **VS Code** with Python and React extensions
- **Git** for version control
- **Docker** for containerized development (optional)

## 🎯 How to Contribute

### 🐛 Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template**
3. **Include detailed information**:
   - OS and version
   - Python/Node.js versions
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

### 💡 Suggesting Features

1. **Check existing feature requests**
2. **Use the feature request template**
3. **Describe the problem** you're trying to solve
4. **Propose a solution** with examples
5. **Consider the scope** and complexity

### 🔧 Contributing Code

#### Types of Contributions

- **Bug fixes**: Fix existing issues
- **Features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **UI/UX**: Improve user interface and experience

#### Contribution Areas

**Backend (Python)**:
- AI assistant improvements
- Document processing enhancements
- Vector store optimizations
- API endpoint additions
- Performance improvements

**Frontend (React/Next.js)**:
- UI component improvements
- User experience enhancements
- Mobile responsiveness
- Accessibility improvements
- New feature interfaces

**Documentation**:
- Installation guides
- Usage tutorials
- API documentation
- Code comments
- README improvements

**Testing**:
- Unit tests
- Integration tests
- E2E tests
- Performance tests
- Security tests

## 🔄 Pull Request Process

### Before Submitting

1. **Create a new branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   # Backend tests
   pytest
   
   # Frontend tests
   cd frontend && npm test
   
   # Manual testing
   # Test your feature thoroughly
   ```

4. **Update documentation** if needed

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   # Follow conventional commit format
   ```

### Submitting the PR

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub

3. **Fill out the PR template** completely

4. **Link any related issues**

### PR Review Process

1. **Automated checks** will run (tests, linting, etc.)
2. **Maintainer review** will be requested
3. **Address feedback** promptly and respectfully
4. **Make requested changes** in new commits
5. **Squash commits** if requested
6. **Merge** once approved

## 📝 Coding Standards

### Python Code Style

- **Follow PEP 8** style guidelines
- **Use type hints** for function parameters and returns
- **Write docstrings** for all functions and classes
- **Keep functions small** and focused
- **Use meaningful variable names**

Example:
```python
def process_document(file_path: str, session_id: str) -> tuple[str, list[str]]:
    """
    Process a document and return text and chunks.
    
    Args:
        file_path: Path to the document file
        session_id: Unique session identifier
        
    Returns:
        Tuple of (full_text, chunks)
    """
    # Implementation here
    pass
```

### JavaScript/TypeScript Code Style

- **Use TypeScript** for type safety
- **Follow ESLint rules** configured in the project
- **Use functional components** with hooks
- **Keep components small** and focused
- **Use meaningful prop names**

Example:
```typescript
interface ChatMessageProps {
  message: string;
  timestamp: string;
  isUser: boolean;
}

export function ChatMessage({ message, timestamp, isUser }: ChatMessageProps) {
  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      {/* Component implementation */}
    </div>
  );
}
```

### Git Commit Messages

Follow **Conventional Commits** format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build/config changes

Examples:
```
feat(chat): add markdown rendering support
fix(upload): resolve PDF parsing error
docs(api): update endpoint documentation
```

## 🧪 Testing

### Running Tests

```bash
# Backend tests
source venv/bin/activate
pytest

# Frontend tests
cd frontend
npm test

# E2E tests (if available)
npm run test:e2e
```

### Writing Tests

- **Write tests** for new features
- **Update tests** when modifying existing code
- **Follow testing best practices**:
  - Test edge cases
  - Use descriptive test names
  - Keep tests isolated
  - Mock external dependencies

### Test Structure

```python
# Backend test example
def test_document_processing():
    """Test that documents are processed correctly."""
    # Arrange
    test_file = "test_document.pdf"
    
    # Act
    result = process_document(test_file)
    
    # Assert
    assert result is not None
    assert len(result.chunks) > 0
```

```typescript
// Frontend test example
describe('ChatMessage', () => {
  it('should render user messages correctly', () => {
    render(
      <ChatMessage 
        message="Hello" 
        timestamp="12:00 PM" 
        isUser={true} 
      />
    );
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

## 📚 Documentation

### Types of Documentation

- **Code comments**: Explain complex logic
- **API documentation**: Document all endpoints
- **User guides**: Help users understand features
- **Developer docs**: Help contributors get started

### Documentation Standards

- **Keep it up to date** with code changes
- **Use clear, simple language**
- **Include examples** and code snippets
- **Add screenshots** for UI features
- **Test documentation** by following it yourself

## 👥 Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Learn from feedback on PRs

### Communication Guidelines

- **Be respectful** and professional
- **Search existing issues** before creating new ones
- **Provide context** when asking questions
- **Help others** when you can
- **Give constructive feedback** in code reviews

## 🏆 Recognition

We appreciate all contributions! Contributors will be:

- **Listed in the README** (if desired)
- **Mentioned in release notes** for significant contributions
- **Given commit access** for consistent, high-quality contributions

## 📧 Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search GitHub issues and discussions
3. Create a new discussion or issue
4. Reach out to maintainers

---

Thank you for contributing to Kensho! Your help makes this project better for everyone. 🌌✨ 