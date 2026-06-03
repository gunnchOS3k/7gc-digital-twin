#!/usr/bin/env python3
try:
    import sionna
    print('sionna: available')
except ImportError:
    print('sionna: not installed (optional)')
