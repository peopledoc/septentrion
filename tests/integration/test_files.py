import pytest

from septentrion import files, versions


def test_iter_dirs(tmp_path):
    (tmp_path / "15.0").mkdir()
    (tmp_path / "16.0").touch()

    assert list(files.iter_dirs(tmp_path)) == [tmp_path / "15.0"]


@pytest.mark.parametrize(
    "ignore_symlinks, expected", [(True, ["16.0"]), (False, ["16.0", "17.0"])]
)
def test_iter_files(tmp_path, ignore_symlinks, expected):
    (tmp_path / "15.0").mkdir()
    (tmp_path / "16.0").touch()
    (tmp_path / "17.0").symlink_to("16.0")

    assert list(files.iter_files(tmp_path, ignore_symlinks=ignore_symlinks)) == [
        tmp_path / e for e in expected
    ]


def test_get_version_migration_dir(tmp_path):
    (tmp_path / "1.0").mkdir()
    (tmp_path / "2.0").mkdir()

    version = versions.Version("2.0")
    assert files.get_version_migration_dir(tmp_path, version).name == "2.0"
