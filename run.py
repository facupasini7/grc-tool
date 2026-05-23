"""Punto de entrada — arranca el servidor desde la raíz del proyecto."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from app import main

if __name__ == "__main__":
    main()
