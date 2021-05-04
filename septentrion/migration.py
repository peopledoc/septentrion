# -*- coding: utf-8 -*-
import io
import logging
import pathlib
import warnings
from typing import List

from septentrion import (
    configuration,
    core,
    db,
    exceptions,
    files,
    runner,
    style,
    utils,
    versions,
)

logger = logging.getLogger(__name__)


def migrate(
    settings: configuration.Settings, stylist: style.Stylist = style.noop_stylist
) -> None:

    logger.info("Starting migrations")

    if not db.is_schema_initialized(settings=settings):
        logger.info("Migration table is empty, loading a schema")
        # schema not inited
        schema_version = core.get_best_schema_version(settings=settings)
        init_schema(settings=settings, init_version=schema_version, stylist=stylist)
        from_version = schema_version
    else:
        _from_version = db.get_current_schema_version(settings=settings)
        assert _from_version  # mypy shenanigans
        from_version = _from_version

    # play migrations
    with stylist.activate("title") as echo:
        echo("Applying migrations")

    for plan in core.build_migration_plan(settings=settings, from_version=from_version):
        version = plan["version"]
        logger.info("Processing version %s", version)
        with stylist.activate("subtitle") as echo:
            echo("Version {}".format(version))
        for mig, applied, path, is_manual in plan["plan"]:
            logger.debug(
                "Processing migration %(mig)s, applied: %(applied)s, "
                "path: %(path)s, manual: %(is_manual)s",
                {"mig": mig, "applied": applied, "path": path, "is_manual": is_manual},
            )
            title = mig
            if is_manual:
                title += " (manual)"
            title += " "
            if applied:
                stylist.draw_checkbox(checked=True, content="Already applied")
                stylist.echo("")  # new line
            else:
                with stylist.checkbox(
                    content="Applying {}...".format(title),
                    content_after="Applied {}".format(title),
                ):
                    run_script(settings=settings, path=path)
                    logger.info("Saving operation in the database")
                    db.write_migration(settings=settings, version=version, name=mig)


def _load_schema_files(settings: configuration.Settings, schema_files: List[str]):
    for file_name in schema_files:
        if not file_name:
            return
        file_path = settings.MIGRATIONS_ROOT / "schemas" / file_name
        logger.info("Loading %s", file_path)
        run_script(settings=settings, path=file_path)


def load_fixtures(
    settings: configuration.Settings,
    init_version: versions.Version,
    stylist: style.Stylist = style.noop_stylist,
) -> None:
    try:
        fixtures_version = core.get_fixtures_version(
            settings=settings, target_version=init_version
        )
        fixtures_path = (
            settings.MIGRATIONS_ROOT
            / "fixtures"
            / settings.FIXTURES_TEMPLATE.format(fixtures_version.original_string)
        )

        with stylist.activate("title") as echo:
            echo("Loading fixtures")
        logger.info("Applying fixture %s (file %s)", fixtures_version, fixtures_path)
        with stylist.checkbox(
            content="Applying fixtures {}...".format(fixtures_version),
            content_after="Applied fixtures {}".format(fixtures_version),
        ):
            run_script(settings=settings, path=fixtures_path)
    except exceptions.SeptentrionException as exception:
        logger.info("Not applying fixtures: %s", exception)


def init_schema(
    settings: configuration.Settings,
    init_version: versions.Version,
    stylist: style.Stylist = style.noop_stylist,
) -> None:
    # load before files
    logger.info("Looking for additional files to run before main schema")
    before_files = settings.BEFORE_SCHEMA_FILE
    _load_schema_files(settings, before_files)

    # load additional files (deprecated)
    logger.info("Looking for additional files to run (deprecated)")
    additional_files = settings.ADDITIONAL_SCHEMA_FILE
    if additional_files:
        warnings.warn(
            "ADDITIONAL_SCHEMA_FILES will be deprecated. "
            "Use BEFORE_SCHEMA_FILES instead."
        )
    _load_schema_files(settings, additional_files)

    # load schema
    with stylist.activate("title") as echo:
        echo("Loading schema")

    schema_path = (
        settings.MIGRATIONS_ROOT
        / "schemas"
        / settings.SCHEMA_TEMPLATE.format(init_version.original_string)
    )

    logger.info("Loading %s", schema_path)

    with stylist.checkbox(
        content="Applying {}...".format(init_version),
        content_after="Applied {}".format(init_version),
    ):

        run_script(settings=settings, path=schema_path)

    create_fake_entries(settings=settings, version=init_version)

    # load after files
    logger.info("Looking for additional files to run after main schema")
    after_files = settings.AFTER_SCHEMA_FILE
    _load_schema_files(settings, after_files)

    # load fixtures
    load_fixtures(settings, init_version, stylist)


def create_fake_entries(
    settings: configuration.Settings,
    version: versions.Version,
    stylist: style.Stylist = style.noop_stylist,
) -> None:
    """
    Write entries in the migration table for all existing migrations
    up until the given version (included).
    """
    # Fake migrations <= init_version
    known_versions = files.get_known_versions(settings=settings)
    versions_to_fake = list(utils.until(known_versions, version))
    logger.info("Will now fake all migrations up to version %s (included)", version)

    with stylist.activate("title") as echo:
        echo("Faking migrations.")

    for version in versions_to_fake:
        logger.info("Faking migrations from version %s", version)
        migrations_to_apply = files.get_migrations_files_mapping(
            settings=settings, version=version
        )
        migs = list(migrations_to_apply)
        migs.sort()
        for migration_name in migs:
            logger.info("Faking %s", migration_name)
            with stylist.checkbox(
                content="Faking {}...".format(migration_name),
                content_after="Faked {}".format(migration_name),
            ):
                db.write_migration(
                    settings=settings, version=version, name=migration_name
                )


def run_script(settings: configuration.Settings, path: pathlib.Path) -> None:
    logger.info("Running SQL file %s", path)
    with io.open(path, "r", encoding="utf8") as f:
        script = runner.Script(settings=settings, file_handler=f, path=path)
        script.run()
