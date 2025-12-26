# Test Maintenance Guide

This guide provides instructions for maintaining and updating the test suite for the Virtual Camera Server application.

## Test Agent Role

The test agent is responsible for:
- Keeping tests updated with code changes
- Validating test health after changes
- Maintaining test documentation
- Ensuring test coverage goals are met

## Test Update Workflow

### 1. After Code Changes

When code is modified, follow these steps:

```bash
# 1. Run test validation
python3 tests/validate_tests.py

# 2. Run affected test suite
pytest tests/unit/          # For service/model changes
pytest tests/integration/    # For workflow changes
pytest tests/user/          # For web interface changes

# 3. Fix any failing tests
# 4. Add new tests for new features
# 5. Run full test suite
pytest

# 6. Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term
```

### 2. Adding New Tests

When adding new features, add corresponding tests:

**For new models:**
- Add tests to `tests/unit/test_models.py`
- Test serialization (`to_dict()`)
- Test deserialization (`from_dict()`)
- Test validation

**For new services:**
- Add tests to `tests/unit/test_<service>_service.py`
- Test all public methods
- Test error cases
- Test edge cases

**For new workflows:**
- Add tests to `tests/integration/test_<workflow>_integration.py`
- Test multi-service interactions
- Test data persistence

**For new web features:**
- Add tests to `tests/user/test_web_interface.py`
- Test user workflows
- Test authentication requirements
- Test error handling

### 3. Test File Structure

Follow the existing structure:

```python
"""Test description."""
import pytest
from src.module import Class

class TestClassName:
    """Tests for ClassName."""
    
    def test_method_name(self, fixture):
        """Test description."""
        # Arrange
        input_data = "test"
        
        # Act
        result = method(input_data)
        
        # Assert
        assert result == expected_value
```

## Test Coverage Goals

### Current Coverage Targets

- **Models**: 100% coverage
- **Services**: >80% coverage (core paths)
- **Web Routes**: >70% coverage (happy paths and error cases)

### Checking Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Common Test Issues

### Issue: Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'cv2'`

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Test Collection Fails

**Symptom**: `ERROR collecting tests/...`

**Solution**:
1. Check dependencies are installed
2. Verify virtual environment is activated
3. Check for syntax errors in test files
4. Run: `python3 tests/validate_tests.py`

### Issue: Tests Fail Due to Directory Issues

**Symptom**: `FileNotFoundError` or `PermissionError`

**Solution**:
- Tests use temporary directories automatically
- If issues persist, check write permissions
- Try: `pytest --basetemp=/tmp/vcamera_tests`

### Issue: Tests Are Slow

**Symptom**: Tests take too long to run

**Solution**:
- Unit tests should be fast (< 1 second each)
- Integration tests may be slower due to video file creation
- If tests hang, check for infinite loops
- Use `pytest -x` to stop on first failure

## Test Documentation Updates

When updating tests, also update:

1. **README.md**: Update test coverage section if new tests added
2. **TEST_PLAN.md**: Update test scenarios if workflows change
3. **TEST_STATUS.md**: Update status after validation
4. **SETUP.md**: Update if setup requirements change

## Test Validation Checklist

Before considering tests complete:

- [ ] All tests pass (`pytest` exits with code 0)
- [ ] No test errors (only failures are acceptable)
- [ ] Coverage goals met
- [ ] Test documentation updated
- [ ] Test validation script passes (`python3 tests/validate_tests.py`)
- [ ] Tests are independent (can run in any order)
- [ ] Tests clean up after themselves (no data pollution)

## Test Categories

### Unit Tests
- Test individual components in isolation
- Fast execution (< 1 second each)
- Use mocks when appropriate
- Test both happy paths and error cases

### Integration Tests
- Test interactions between components
- May be slower due to file I/O
- Test complete workflows
- Test data persistence

### User/End-to-End Tests
- Test complete user workflows
- Test through web interface
- Test authentication requirements
- Test error handling from user perspective

## Best Practices

1. **Test Independence**: Tests should not depend on each other
2. **Test Isolation**: Each test should clean up after itself
3. **Clear Names**: Test names should clearly describe what they test
4. **Arrange-Act-Assert**: Follow AAA pattern in tests
5. **One Assert Per Test**: Focus each test on one behavior
6. **Fast Tests**: Keep tests fast to encourage frequent execution
7. **Documentation**: Document complex test scenarios

## Test Maintenance Schedule

### After Each Code Change
- Run affected test suite
- Fix any failing tests
- Add tests for new features

### Before Commits
- Run full test suite
- Verify all tests pass
- Check coverage hasn't decreased

### Weekly
- Run full test suite with coverage
- Review test status
- Update test documentation if needed

### Monthly
- Review test coverage goals
- Identify gaps in test coverage
- Plan new test additions

## Getting Help

For test-related questions:
- See `tests/README.md` for test documentation
- See `tests/SETUP.md` for setup issues
- See `tests/TEST_PLAN.md` for test strategy
- See `tests/TEST_STATUS.md` for current status

