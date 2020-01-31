import pytest

from septentrion import files


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
