import importlib_metadata

from septentrion import metadata


def test_extract_metadata(mocker):
    patch = mocker.patch(
        "importlib_metadata.metadata",
        return_value={
            "Author": "a",
            "Author-email": "b",
            "License": "c",
            "Home-page": "d",
            "Version": "e",
        },
    )
    assert metadata.extract_metadata("septentrion") == {
        "author": "a",
        "email": "b",
        "license": "c",
        "url": "d",
        "version": "e",
    }
    patch.assert_called_once_with("septentrion")


def test_extract_metadata_error(mocker):
    mocker.patch(
        "importlib_metadata.metadata",
        side_effect=importlib_metadata.PackageNotFoundError,
    )

    assert metadata.extract_metadata("septentrion") == {
        "author": "-",
        "email": "-",
        "license": "-",
        "url": "-",
        "version": "0.0.0",
    }
