import os
import shutil
from pathlib import Path
from typing import Set


def copy_content(subdir: str, allowed_extensions: Set[str], exclude: Set[str] = ()):
    src_dir = Path(os.environ['SPACE_ENGINEERS_ROOT']) / 'Content' / subdir
    dst_dir = Path('Content') / subdir
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src_path in src_dir.glob('**/*'):
        src_path_ext = str(src_path).rsplit('.', 1)[-1].lower()
        if src_path_ext not in allowed_extensions:
            continue

        if any(part in exclude for part in str(src_path).split(os.sep)):
            continue

        dst_path = dst_dir / src_path.relative_to(src_dir)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_path, dst_path)


def main():
    copy_content('CustomWorlds', {'scf'})
    copy_content('Data', {'sbc', 'sbl', 'resx', 'vs', 'gsc', 'json'}, {'Prefabs'})
    copy_content('DataPlatform', {'json'})
    copy_content('Fonts', {'xml'})
    copy_content('Particles', {'mwl'})
    copy_content('Scenarios', {'scf', 'sbl', 'resx', 'vs'})
    copy_content('Shaders', {'hlsi'})
    copy_content('VisualScripts', {'vs', 'vsc', 'sbl', 'resx'})


if __name__ == '__main__':
    main()
