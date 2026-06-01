# Package marker for src
# Dynamically adds the src directory to sys.path to allow absolute imports of shared and agents
import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
