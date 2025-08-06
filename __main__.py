#!/usr/bin/env python3
"""
BrowserTest AI - Module entry point

Allows running the framework as a Python module:
    python -m . run test_suites/examples/example_test_suite.yaml
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import main

if __name__ == "__main__":
    main()