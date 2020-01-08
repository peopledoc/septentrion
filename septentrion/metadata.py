from typing import Mapping

import importlib_metadata


def extract_metadata(package_name: str) -> Mapping[str, str]:

    # Backport of Python 3.8's future importlib.metadata()
    try:
        metadata = importlib_metadata.metadata(package_name)
    except importlib_metadata.PackageNotFoundError:
        return {
            "author": "-",
            "email": "-",
            "license": "-",
            "url": "-",
            "version": "0.0.0",
        }

    return {
        "author": metadata["Author"],
        "email": metadata["Author-email"],
        "license": metadata["License"],
        "url": metadata["Home-page"],
        "version": metadata["Version"],
    }
