import sys
from .console import Console
console = Console()
sys.exit(0) if console() else sys.exit(1)