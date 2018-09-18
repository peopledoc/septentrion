import pkg_resources

from west import _extract_version


def test_extract_version(mocker):
    mocker.patch(
        "pkg_resources.get_distribution", return_value=mocker.Mock(version="0.1")
    )
    version = _extract_version("west")
    assert version == "0.1"


def test_extract_version_ko(mocker):
    mocker.patch(
        "pkg_resources.get_distribution", side_effect=pkg_resources.DistributionNotFound
    )
    assert _extract_version("west") == "not_installed"
