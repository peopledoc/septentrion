from septentrion import configuration, core, migrate as migrate_module, style, versions


def lib_kwargs(settings_kwargs):
    quiet = settings_kwargs.pop("quiet", False)
    stylist = style.noop_stylist if quiet else style.stylist
    settings = configuration.Settings(**settings_kwargs)
    return {"settings": settings, "stylist": stylist}


def show_migrations(**settings_kwargs):
    core.describe_migration_plan(**lib_kwargs(settings_kwargs))


def migrate(*, migration_applied_callback=None, **settings_kwargs):
    migration.migrate(
        migration_applied_callback=migration_applied_callback,
        **lib_kwargs(settings_kwargs)
    )


def fake(version: str, **settings_kwargs):
    fake_version = versions.Version.from_string(version)
    migrate_module.create_fake_entries(
        version=fake_version, **lib_kwargs(settings_kwargs)
    )
