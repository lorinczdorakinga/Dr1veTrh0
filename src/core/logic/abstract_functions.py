from pathlib import Path
import sys

def get_resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent
        base_path = base_path.parent.parent  # Go up to the root of the project
    path = base_path / 'assets' / relative_path
    if not path.exists():
        print (path)
        print(f"Warning: Resource {relative_path} not found.")
        return str(base_path / "img/default.png")
    return str(path)