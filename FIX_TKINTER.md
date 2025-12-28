# Fix: ModuleNotFoundError: No module named 'tkinter'

## Problem

When running the application, you see:
```
ModuleNotFoundError: No module named 'tkinter'
```

## Cause

tkinter is part of Python's standard library, but on Linux it's provided by a separate system package (`python3-tk`). It cannot be installed via pip.

## Solution

Install the `python3-tk` system package:

```bash
sudo apt-get install -y python3-tk
```

## Verify

After installing, verify tkinter is available:

```bash
python3 -c "import tkinter; print('tkinter OK')"
```

Should output "tkinter OK".

## Then Run Application

```bash
source venv/bin/activate
python src/main.py
```

## Note

Even though tkinter is "standard library", on Linux distributions it's often packaged separately to keep the base Python installation minimal. This is normal and expected.

