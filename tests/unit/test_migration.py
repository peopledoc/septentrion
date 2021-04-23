from septentrion import configuration, migration


def test_migrate_uses_correct_version_with_db(mocker):
    mocker.patch("septentrion.db.is_schema_initialized", return_value=True)
    mock_init_schema = mocker.patch("septentrion.migration.init_schema")
    current_version = mocker.patch("septentrion.db.get_current_schema_version")

    build_migration_plan = mocker.patch(
        "septentrion.migration.core.build_migration_plan",
        return_value=[],
    )

    settings = configuration.Settings(
        host="",
        port="",
        username="",
        dbname="",
        migrations_root="example_migrations",
        target_version=None,
    )

    migration.migrate(settings=settings)

    mock_init_schema.assert_not_called()
    build_migration_plan.assert_called_with(
        settings=settings, from_version=current_version.return_value
    )


def test_migrate_uses_correct_version_without_db(mocker):
    mocker.patch("septentrion.db.is_schema_initialized", return_value=False)
    mock_init_schema = mocker.patch("septentrion.migration.init_schema")
    mocker.patch("septentrion.db.get_current_schema_version")
    schema_version = mocker.patch("septentrion.core.get_best_schema_version")

    build_migration_plan = mocker.patch(
        "septentrion.migration.core.build_migration_plan",
        return_value=[],
    )

    settings = configuration.Settings(
        host="",
        port="",
        username="",
        dbname="",
        migrations_root="example_migrations",
        target_version=None,
    )

    migration.migrate(settings=settings)

    mock_init_schema.assert_called_once()
    build_migration_plan.assert_called_with(
        settings=settings, from_version=schema_version.return_value
    )
