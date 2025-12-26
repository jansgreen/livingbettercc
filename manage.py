#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Force the correct settings module for this project.
    # Using setdefault() can be overridden by an external environment variable
    # (e.g. DJANGO_SETTINGS_MODULE=vargmelo.settings), which leads to confusing 404s.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'livingbettercc.settings'
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
