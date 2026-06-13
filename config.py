from pathlib import Path
import shutil

# bronbestand in je repo (read-only backup)
SOURCE = Path(__file__).resolve().parent / "data.xlsx"

# runtime bestand (hier wordt alles in geschreven)
DATA = Path("/tmp/data.xlsx")

def init_data():
    if not DATA.exists():
        shutil.copy(SOURCE, DATA)
