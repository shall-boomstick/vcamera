# Test Suite: Virtual Camera Server

This directory contains the test suite for the Virtual Camera Server application, covering Phases 1-4.

## Quick Status

For current test status and validation, see:
- **[TEST_STATUS.md](TEST_STATUS.md)** - Current test status and health report
- **[validate_tests.py](validate_tests.py)** - Test validation script

Run validation: `python3 tests/validate_tests.py`

## Test Structure

```
tests/
├── unit/              # Unit tests for individual components
│   ├── test_models.py
│   ├── test_storage.py
│   ├── test_auth_service.py
│   ├── test_video_library_service.py
│   └── test_camera_manager_service.py
├── integration/      # Integration tests for service interactions
│   ├── test_video_library_integration.py
│   ├── test_camera_lifecycle.py
│   └── test_auth_integration.py
├── user/             # End-to-end user workflow tests
│   └── test_web_interface.py
├── conftest.py       # Shared pytest fixtures
└── README.md         # This file
```

## Running Tests

### Run All Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies
# Validate test health
python3 tests/validate_tests.py

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Check test collection
pytest --collect-only
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# User/End-to-end tests only
pytest tests/user/

# Specific test file
pytest tests/unit/test_models.py

# Specific test class
pytest tests/unit/test_models.py::TestVideo

# Specific test method
pytest tests/unit/test_models.py::TestVideo::test_video_creation
```

## Test Coverage

### Phase 1: Setup
- ✅ Project structure validation (manual)
- ✅ Requirements.txt validation (manual)

### Phase 2: Foundational
- ✅ Storage utilities (read_json, write_json, ensure_directories)
- ✅ Exception classes
- ✅ UUID generation
- ✅ Directory initialization

### Phase 3: User Story 1 (MVP)
- ✅ Video model serialization/deserialization
- ✅ VirtualCamera model serialization/deserialization
- ✅ VideoLibraryService (upload, get, list, file path)
- ✅ CameraManagerService (create, get, list, update, delete)
- ✅ Video metadata extraction
- ✅ Camera creation with validation

### Phase 4: User Story 2 (Web Interface)
- ✅ UserSession model
- ✅ AuthService (create credentials, authenticate, validate session, logout)
- ✅ Web authentication flow
- ✅ Web video upload (requires auth)
- ✅ Web camera management (requires auth)
- ✅ Dashboard access control

## Test Categories

### Unit Tests
Test individual components in isolation:
- **Models**: Data serialization, deserialization, validation
- **Services**: Business logic, error handling, edge cases
- **Utilities**: Helper functions, storage operations

### Integration Tests
Test interactions between components:
- **Video Library**: Upload → Retrieve → List workflow
- **Camera Lifecycle**: Create → Update → Delete workflow
- **Authentication**: Create credentials → Login → Validate → Logout workflow
- **Service Integration**: VideoLibrary + CameraManager interactions

### User/End-to-End Tests
Test complete user workflows through web interface:
- **Authentication Flow**: Create credentials → Login → Access dashboard → Logout
- **Video Upload**: Login → Upload video → Verify in library
- **Camera Management**: Login → Create camera → View camera list
- **Access Control**: Verify authentication required for all operations

## Test Fixtures

Common fixtures defined in `conftest.py`:
- `temp_dir`: Temporary directory for test data
- `test_data_dir`: Test data directory structure
- `video_library_service`: VideoLibraryService instance with test data
- `camera_manager_service`: CameraManagerService instance
- `auth_service`: AuthService instance with test data
- `test_client`: Flask test client for web interface tests

## Writing New Tests

### Unit Test Example

```python
def test_feature_name(service_fixture):
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = service_fixture.method(input_data)
    
    # Assert
    assert result == expected_value
```

### Integration Test Example

```python
def test_workflow_name(service1, service2):
    """Test multi-service workflow."""
    # Setup
    item = service1.create_item()
    
    # Execute
    result = service2.use_item(item.id)
    
    # Verify
    assert result is not None
```

### User Test Example

```python
def test_user_workflow(test_client):
    """Test user workflow through web interface."""
    # Login
    test_client.post('/auth/login', data={'username': 'user', 'password': 'pass'})
    
    # Perform action
    response = test_client.post('/api/action', json={'data': 'value'})
    
    # Verify
    assert response.status_code == 200
```

## Notes

- Tests use temporary directories to avoid polluting the main data directory
- Video tests create minimal test videos using OpenCV
- Web tests use Flask's test client (no actual server required)
- RTSP streaming tests are not included (requires GStreamer and actual streaming)

## Test Validation

### Quick Validation

Run the test validation script to check test health:

```bash
python3 tests/validate_tests.py
```

This will check:
- All test files are present
- Dependencies are installed
- Tests can be collected
- Test structure is correct

### Manual Validation

```bash
# Check test collection (no execution)
pytest --collect-only

# Run a quick smoke test
pytest tests/unit/test_models.py -v
```

## Test Maintenance

### When Tests Need Updates

Tests should be updated when:
- New features are added
- Existing features are modified
- Bugs are fixed
- Code is refactored
- Test failures occur

### Test Update Process

1. Identify affected test files
2. Update test cases to match new behavior
3. Add new test cases for new features
4. Run full test suite: `pytest`
5. Generate coverage report: `pytest --cov=src --cov-report=html`
6. Update test documentation if needed
7. Verify all tests pass

### Test Agent Responsibilities

The test agent (this system) is responsible for:
- ✅ Maintaining test documentation
- ✅ Validating test structure
- ✅ Ensuring tests stay updated with code changes
- ✅ Monitoring test health
- ✅ Reporting test status
- ✅ Updating test documentation

## Future Test Additions

- RTSP streaming integration tests (requires GStreamer setup)
- Performance tests (concurrent streams, large file uploads)
- Security tests (authentication bypass, session hijacking)
- Browser-based end-to-end tests (Selenium/Playwright)

