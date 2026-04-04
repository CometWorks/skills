import os
import shutil
import sys
from pathlib import Path
from typing import Set

def copy_content(original_content_dir: Path, subdir: str, allowed_extensions: Set[str], exclude: Set[str] = ()):
    src_dir = original_content_dir / subdir
    assert src_dir.is_dir()
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
    oc = Path(sys.argv[1])
    assert oc.is_dir()
    copy_content(oc, 'CustomWorlds', {'scf'})
    copy_content(oc, 'Data', {'sbc', 'sbl', 'resx', 'vs', 'gsc', 'json'}, {'Prefabs'})
    copy_content(oc, 'DataPlatform', {'json'})
    copy_content(oc, 'Fonts', {'xml'})
    copy_content(oc, 'Particles', {'mwl'})
    copy_content(oc, 'Scenarios', {'scf', 'sbl', 'resx', 'vs'})
    copy_content(oc, 'Shaders', {'hlsl'})
    copy_content(oc, 'VisualScripts', {'vs', 'vsc', 'sbl', 'resx'})


if __name__ == '__main__':
    main()
