def _extract_version(package_name):
    try:
        # Package is installed (even with -e)
        import pkg_resources
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        # Package is in the current directory or in the python path
        from setuptools.config import read_configuration
        from os import path as _p
        _conf = read_configuration(
            _p.join(_p.dirname(_p.dirname(__file__)),
                    "setup.cfg"))
        return _conf["metadata"]["version"]


__version__ = _extract_version("west")
