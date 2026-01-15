"""GUI module for VoltGuard."""
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.app import CableSizingApp

__all__ = ["CableSizingApp"]
