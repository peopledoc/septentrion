"""
Interact with the migration files.
"""

import pathlib
from typing import Dict, Iterable, List, Tuple

from septentrion import configuration, exceptions, utils, versions


def iter_dirs(root: pathlib.Path) -> Iterable[pathlib.Path]:
    return (d for d in sorted(root.iterdir()) if d.is_dir())


def iter_files(
    root: pathlib.Path, ignore_symlinks: bool = False
) -> Iterable[pathlib.Path]:
    for f in sorted(root.iterdir()):
        if not f.is_file():
            continue
        if ignore_symlinks and f.is_symlink():
            continue
        yield f


def get_known_versions(settings: configuration.Settings) -> List[versions.Version]:
    """
    Return the list of the known versions defined in migration repository,
    ordered.
    Ignore symlinks.
    """
    # exclude symlinks and some folders (like schemas, fixtures, etc)
    try:
        folders_names = [str(d.name) for d in iter_dirs(settings.MIGRATIONS_ROOT)]
    except OSError:
        raise exceptions.SeptentrionException(
            "settings.MIGRATIONS_ROOT is improperly configured."
        )

    return sorted(
        versions.Version.from_string(name)
        for name in folders_names
        if utils.is_version(name)
    )


def is_manual_migration(
    migration_path: pathlib.Path, migration_contents: Iterable[str]
) -> bool:

    if "manual" in migration_path.parts:
        return True

    if not migration_path.suffixes[-2:] == [".dml", ".sql"]:
        return False

    for line in migration_contents:
        if "--meta-psql:" in line:
            return True

    return False


# TODO: remove this function when get_best_schema_version is refactored
def get_special_files(root: pathlib.Path, folder: str) -> List[str]:
    try:
        return [str(f.name) for f in iter_files(root / folder)]
    except FileNotFoundError:
        return []


def get_migrations_files_mapping(
    settings: configuration.Settings, version: versions.Version
) -> Dict[str, pathlib.Path]:
    """
    Return an dict containing the list of migrations for
    the given version.
    Key: name of the migration.
    Value: path to the migration file.
    """
    ignore_symlinks = settings.IGNORE_SYMLINKS

    version_root = settings.MIGRATIONS_ROOT / version.original_string
    migrations = {}

    # TODO: should be a setting
    subfolders = [".", "manual"]
    for subfolder_name in subfolders:
        subfolder = version_root / subfolder_name
        if not subfolder.exists():
            continue
        for mig, path in list_migrations_and_paths(
            folder=subfolder, ignore_symlinks=ignore_symlinks
        ):
            migrations[mig] = path

    return migrations


def list_migrations_and_paths(
    folder: pathlib.Path, ignore_symlinks: bool
) -> Iterable[Tuple[str, pathlib.Path]]:

    for file in iter_files(root=folder, ignore_symlinks=ignore_symlinks):
        if not file.suffix == ".sql" or not file.stem[-3:] in ("ddl", "dml"):
            continue

        yield file.name, file


def file_lines_generator(path: pathlib.Path):
    with open(path) as f:
        for line in f:
            yield line
