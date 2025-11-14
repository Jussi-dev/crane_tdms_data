# Contributing to TDMS Channel Selector

Thank you for your interest in contributing to the TDMS Channel Selector project!

## 🚀 Getting Started

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone [repository-url]
   cd crane_tdms_data
   ```

2. **Install dependencies**:
   ```bash
   pip install pandas nptdms
   ```

3. **Run the application**:
   ```bash
   python tdms_viewer.py
   ```

## 🌿 Branch Strategy

### Main Branches
- **`main`**: Stable, production-ready code with version tags
- **`feature/*`**: New feature development branches
- **`bugfix/*`**: Bug fix branches
- **`hotfix/*`**: Critical fixes for production issues

### Current Development
- **`feature/multi-file-support`**: Adding support for multiple TDMS files

### Workflow

1. **Create Feature Branch**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**:
   - Write clean, documented code
   - Follow existing code style
   - Test thoroughly

3. **Update Documentation**:
   - Update `CHANGELOG.md` with your changes
   - Update `README.md` if needed
   - Add docstrings for new functions

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

5. **Create Pull Request**:
   - Merge target: `main`
   - Include description of changes
   - Reference any related issues

## 📝 Coding Standards

### Python Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Keep functions focused and single-purpose

### Example Function Documentation:
```python
def process_channels(self, channel_list):
    """
    Process a list of channels for export.
    
    Args:
        channel_list (list): List of channel display names
        
    Returns:
        dict: Processed channel data ready for CSV export
        
    Raises:
        ValueError: If channel_list is empty
    """
```

### Git Commit Messages
Use clear, descriptive commit messages:

- **Add**: New features or files
- **Fix**: Bug fixes
- **Update**: Changes to existing functionality  
- **Remove**: Deleted features or files
- **Refactor**: Code restructuring without functional changes

Examples:
```bash
git commit -m "Add: Multi-file selection dialog"
git commit -m "Fix: Memory leak in channel loading"
git commit -m "Update: Improve error handling for invalid TDMS files"
```

## 🧪 Testing Guidelines

### Before Submitting
1. **Functional Testing**:
   - Test with various TDMS file formats
   - Verify all export options work correctly
   - Test error handling with invalid files

2. **UI Testing**:
   - Check resizing behavior
   - Verify all buttons and controls work
   - Test with different screen resolutions

3. **Performance Testing**:
   - Test with large TDMS files
   - Monitor memory usage
   - Check load times

### Test Files
- Use representative TDMS files for testing
- Test edge cases (empty files, corrupted data)
- Verify cross-platform compatibility

## 📋 Code Review Checklist

### Functionality
- [ ] New features work as described
- [ ] Existing functionality remains intact
- [ ] Error handling is appropriate
- [ ] Performance is acceptable

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Functions are well-documented
- [ ] Variable names are meaningful
- [ ] No unnecessary code duplication

### Documentation
- [ ] CHANGELOG.md updated
- [ ] README.md updated if needed
- [ ] Code comments explain complex logic
- [ ] Docstrings added for new functions

## 🐛 Reporting Issues

### Bug Reports
Include the following information:
- Operating system and Python version
- Steps to reproduce the issue
- Expected vs. actual behavior
- Error messages or screenshots
- Sample TDMS files (if applicable)

### Feature Requests
Provide:
- Clear description of the desired feature
- Use case and benefits
- Proposed implementation approach
- Any relevant examples or mockups

## 🏷️ Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **Major** (v2.0.0): Breaking changes
- **Minor** (v1.1.0): New features, backwards compatible
- **Patch** (v1.0.1): Bug fixes, backwards compatible

### Release Steps
1. Update version number in code
2. Update CHANGELOG.md
3. Create release tag
4. Update documentation
5. Test thoroughly

## 💡 Development Tips

### GUI Development
- Use ttk widgets for consistent styling
- Follow the existing layout patterns
- Test UI scaling on different screen sizes
- Ensure keyboard navigation works

### Performance Optimization
- Profile code for bottlenecks
- Use generators for large datasets
- Implement progress indicators for long operations
- Consider memory usage with large files

### Error Handling
- Provide user-friendly error messages
- Log detailed errors for debugging
- Gracefully handle edge cases
- Never crash without explanation

## 🤝 Questions?

Feel free to reach out if you have questions about:
- Development setup
- Code architecture  
- Feature implementation
- Testing procedures

Happy coding! 🎉