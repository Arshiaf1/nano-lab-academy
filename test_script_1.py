#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from app.main import app

print('=== Route Paths ===')
paths = app.route_paths()
for path in paths:
    print(f'  {path}')
print(f'Total routes: {len(paths)}')
