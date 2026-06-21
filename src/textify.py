#!/usr/bin/env python

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import shutil
from typing import Iterable

EXTENSIONS: tuple[str, ...] = (
    'py',
    'md',
)

EXCLUDED_FILES: set[str] = {
    'textify.py',
}


def copy_file(source_path: Path, target_path: Path):
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)
    print(f'Copied: {source_path} -> {target_path}')


def textify(extensions: Iterable[str], max_workers: int = 8):
    extensions = [ext.lower().lstrip('.') for ext in extensions]

    source_root = Path.cwd()
    target_root = source_root / 'Textified'

    tasks = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for path in source_root.rglob('*'):
            # Skip the output directory to avoid infinite recursion
            if target_root in path.parents:
                continue

            if path.is_file():
                # Skip the output of this file.
                if path.resolve() == Path(__file__).resolve():
                    continue

                # Skip EXCLUDED_FILES
                if path.name in EXCLUDED_FILES:
                    continue

                lower_name = path.name.lower()

                for ext in extensions:
                    if lower_name.endswith('.' + ext):
                        rel_dir = path.parent.relative_to(source_root)
                        target_dir = target_root / rel_dir

                        new_name = path.name + '.txt'
                        target_path = target_dir / new_name

                        # Submit copy task to thread pool
                        tasks.append(executor.submit(copy_file, path, target_path))
                        break  # No need to check other extensions

    # Ensure all tasks complete
    for t in tasks:
        t.result()


if __name__ == '__main__':
    textify(EXTENSIONS)
    print('Done.')
