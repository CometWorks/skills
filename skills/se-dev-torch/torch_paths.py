"""
Shared path resolution for the Torch skill.

All persistent skill data lives under the Data symlink/junction inside the
skill folder.
"""

from pathlib import Path


SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / "Data"
SOURCES_DIR = DATA_DIR / "Sources"
TORCH_CLONE_DIR = SOURCES_DIR / "Torch"
CODE_INDEX_DIR = DATA_DIR / "CodeIndex"
TORCH_ROOT_FILE = DATA_DIR / "torch_root.txt"


def get_torch_root() -> Path:
    """Return the configured Torch source root."""
    if not TORCH_ROOT_FILE.exists():
        raise FileNotFoundError(
            f"{TORCH_ROOT_FILE} not found. Run Prepare.bat / Prepare.sh first."
        )

    root_text = TORCH_ROOT_FILE.read_text(encoding="utf-8").strip()
    if not root_text:
        raise RuntimeError(
            f"{TORCH_ROOT_FILE} is empty. Run Prepare.bat / Prepare.sh again."
        )

    root = Path(root_text).expanduser()
    if not root.exists():
        raise FileNotFoundError(
            f"Configured Torch source root does not exist: {root}"
        )
    if not (root / "Torch.sln").exists():
        raise FileNotFoundError(
            f"Configured Torch source root is missing Torch.sln: {root}"
        )
    return root
