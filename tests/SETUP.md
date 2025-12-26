# Test Setup Guide

## Prerequisites

Before running tests, ensure you have:

1. **Virtual environment activated**
   ```bash
   source venv/bin/activate
   ```

2. **All dependencies installed**
   ```bash
   pip install -r requirements.txt
   ```

   This includes:
   - `opencv-python` (for video processing)
   - `Flask` (for web interface)
   - `pytest` (for testing framework)
   - `pytest-cov` (for coverage reports)

## Common Setup Issues

### Issue: `ModuleNotFoundError: No module named 'cv2'`

**Solution**: Install opencv-python
```bash
pip install opencv-python
```

### Issue: `FileNotFoundError: [Errno 2] No such file or directory` in `os.getcwd()`

**Solution**: This is handled in the test fixtures. If you still see this:
1. Ensure you're running tests from the project root directory
2. The fixtures now have fallback handling for this case

### Issue: `ModuleNotFoundError: No module named 'pytest'`

**Solution**: Install pytest
```bash
pip install pytest pytest-cov
```

## Verifying Setup

Run a simple test to verify everything is set up:

```bash
# Test that pytest can import modules
python3 -c "import pytest; print('pytest OK')"

# Test that opencv is available
python3 -c "import cv2; print('opencv OK')"

# Test that Flask is available
python3 -c "import flask; print('Flask OK')"

# Run a simple test
pytest tests/unit/test_models.py::TestVideo::test_video_creation -v
```

## Running Tests

Once setup is complete:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_models.py

# Run with coverage
pytest --cov=src --cov-report=html
```

## Troubleshooting

### Tests fail with import errors

1. Ensure virtual environment is activated
2. Install all dependencies: `pip install -r requirements.txt`
3. Verify imports work: `python3 -c "from src.services import VideoLibraryService"`

### Tests fail with directory errors

The test fixtures now handle directory issues automatically. If problems persist:
1. Ensure you have write permissions in the temp directory
2. Check that `/tmp` is accessible
3. Try running tests with `--basetemp` option:
   ```bash
   pytest --basetemp=/tmp/vcamera_tests
   ```

### Tests are slow

- Unit tests should be fast (< 1 second each)
- Integration tests may be slower due to video file creation
- If tests hang, check for infinite loops or blocking operations

