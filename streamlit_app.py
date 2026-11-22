"""Streamlit Cloud standard entrypoint."""
import os
import sys
from pathlib import Path

# Add repo root to path
_REPO_ROOT = str(Path(__file__).resolve().parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Load and execute app/main.py
_main_path = Path(__file__).resolve().parent / "app" / "main.py"
with open(_main_path, "r", encoding="utf-8") as _f:
    _code = compile(_f.read(), str(_main_path), "exec")
    exec(_code, globals())
