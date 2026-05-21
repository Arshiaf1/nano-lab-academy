"""nano-lab-academy application package."""
import os
import sys

# Automatically setup frontend on import if needed
try:
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    if not os.path.exists(frontend_path):
        setup_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup-frontend.py')
        if os.path.exists(setup_script):
            exec(open(setup_script).read(), {'__name__': '__main__'})
except Exception as e:
    pass  # Silently fail if setup doesn't work
