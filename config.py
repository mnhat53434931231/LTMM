from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
KEYS_DIR = BASE_DIR / 'keys'
DB_PATH = DATA_DIR / 'wallet.db'
DATA_DIR.mkdir(exist_ok=True); KEYS_DIR.mkdir(exist_ok=True)
