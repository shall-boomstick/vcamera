# Fix: girepository-2.0 Not Found Error

## Current Error

```
Run-time dependency girepository-2.0 found: NO (tried pkgconfig and cmake)
ERROR: Dependency 'girepository-2.0' is required but not found.
```

## Solution

Install the missing `libgirepository-2.0-dev` package:

```bash
sudo apt-get install -y libgirepository-2.0-dev gobject-introspection
```

This package provides the pkg-config files that PyGObject needs to find the GObject Introspection library.

## Verify Installation

After installing, verify pkg-config can find it:

```bash
pkg-config --exists girepository-2.0 && echo "Found!" || echo "Still missing"
```

Should output "Found!".

## Then Retry pip install

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Complete Package List

If you want to install everything at once:

```bash
sudo apt-get update && sudo apt-get install -y \
    python3-dev \
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

