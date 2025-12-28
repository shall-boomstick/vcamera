# Quick Fix: Common Installation Errors

## Error 1: PyGObject Installation - Missing Dependencies

### Problem

You're seeing this error when running `pip install -r requirements.txt`:

```
ERROR: Dependency lookup for cairo with method 'pkgconfig' failed: Pkg-config for machine host machine not found.
```

OR

```
ERROR: Dependency 'girepository-2.0' is required but not found.
```

### Solution

PyGObject requires system-level packages that must be installed BEFORE pip can install PyGObject.

**Install all required system dependencies:**

```bash
sudo apt-get update && sudo apt-get install -y \
    python3-dev \
    python3-tk \
    pkg-config \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-rtsp-server-1.0 \
    libcairo2-dev \
    libgirepository1.0-dev \
    libgirepository-2.0-dev \
    gobject-introspection \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    libgstreamer1.0-dev \
    libgstrtspserver-1.0-dev
```

**Key packages**:
- `libgirepository-2.0-dev` - Provides pkg-config files for girepository-2.0
- `python3-tk` - Provides tkinter (GUI framework)

### Verify Installation

```bash
# Check pkg-config
pkg-config --version

# Check tkinter
python3 -c "import tkinter; print('tkinter OK')"

# Check girepository
pkg-config --exists girepository-2.0 && echo "girepository OK" || echo "girepository missing"
```

### Retry pip install

```bash
source venv/bin/activate  # If not already activated
pip install -r requirements.txt
```

---

## Error 2: ModuleNotFoundError: No module named 'tkinter'

### Problem

When running the application:
```
ModuleNotFoundError: No module named 'tkinter'
```

### Solution

tkinter is provided by the `python3-tk` system package (not installable via pip):

```bash
sudo apt-get install -y python3-tk
```

### Verify

```bash
python3 -c "import tkinter; print('tkinter OK')"
```

Should output "tkinter OK".

### Then Run Application

```bash
source venv/bin/activate
python src/main.py
```

---

## Why These Happen

### PyGObject

PyGObject (Python GObject Introspection) is a Python binding for the GObject library system. It requires:
- **pkg-config**: Tool to find installed libraries
- **cairo**: Graphics library (development headers)
- **gobject-introspection**: System to generate Python bindings
- **GStreamer**: Multimedia framework (for RTSP)

These are system-level packages that can't be installed via pip.

### tkinter

Even though tkinter is "standard library", on Linux distributions it's often packaged separately (`python3-tk`) to keep the base Python installation minimal. This is normal and expected.

---

## Complete Installation Command

To install everything at once:

```bash
sudo apt-get update && sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-tk \
    pkg-config \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-rtsp-server-1.0 \
    libcairo2-dev \
    libgirepository1.0-dev \
    libgirepository-2.0-dev \
    gobject-introspection \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    libgstreamer1.0-dev \
    libgstrtspserver-1.0-dev
```

Then:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
