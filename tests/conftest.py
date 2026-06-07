"""Shared pytest setup for Kivy-based imports."""

import os

# Avoid Kivy parsing CLI args when tests import demo or kivmob.
os.environ.setdefault("KIVY_NO_ARGS", "1")
