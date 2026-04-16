"""
Pytest configuration with stubs for missing dependencies.
Run with: pytest -v
Or skip integration tests: pytest -v -m "not integration"
"""

import sys
from unittest.mock import MagicMock, Mock

# Stub for selenium module
if "selenium" not in sys.modules:
    sys.modules["selenium"] = MagicMock()

# Stub for playwright module
if "playwright" not in sys.modules:
    sys.modules["playwright"] = MagicMock()


# Stub for langchain modules with lazy loading
class LazyLangChainStub:
    def __getattr__(self, name):
        return MagicMock()

    def __call__(self, *args, **kwargs):
        return MagicMock()


# Only stub when langchain has import errors
try:
    from langchain_core import _api
except (ImportError, ModuleNotFoundError):
    sys.modules["langchain_core._api"] = MagicMock()
    sys.modules["langchain_core.documents"] = MagicMock()
