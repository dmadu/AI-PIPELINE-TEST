"""API blueprint package.

Blueprints live in sibling modules (``health.py`` today, ``auth.py`` later) and are registered
by the application factory in :mod:`app`. Nothing is imported here to keep the package free of
import-time side effects and circular imports.
"""
