#!/usr/bin/env python3
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dust2cash.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and available on your PYTHONPATH environment variable. "
            "Activate your virtual environment and try again."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
