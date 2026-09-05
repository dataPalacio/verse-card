import sys
from pathlib import Path

# garante que 'pipeline' seja importavel rodando a partir da raiz do projeto
RAIZ = Path(__file__).resolve().parent.parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
