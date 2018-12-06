def _extract_version(package_name):
    try:
        # Package is installed (even with -e)
        import pkg_resources

        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return "not_installed"


__version__ = _extract_version("septentrion")
