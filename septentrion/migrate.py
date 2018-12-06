# -*- coding: utf-8 -*-
import io
import logging
import os.path

from septentrion import core
from septentrion import db
from septentrion import exceptions
from septentrion import files
from septentrion import runner
from septentrion import style
from septentrion import utils
from septentrion.settings import settings

logger = logging.getLogger(__name__)


def migrate(stylist=style.noop_stylist):

    logger.info("Starting migrations")
    if not db.is_schema_initialized():
        logger.info("Migration table is empty, loading a schema")
        # schema not inited
        schema_version = core.get_best_schema_version()
        init_schema(schema_version, stylist=stylist)

    # play migrations
    with stylist.activate("title") as echo:
        echo("Applying migrations")

    for plan in core.build_migration_plan():
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
                stylist.draw_checkbox(
                    checked=True, content="Already applied".format(title)
                )
                stylist.echo("")  # new line
            else:
                with stylist.checkbox(
                    content="Applying {}...".format(title),
                    content_after="Applied {}".format(title),
                ):
                    run_script(path)
                    logger.info("Saving operation in the database")
                    db.write_migration(version, mig)


def init_schema(init_version, stylist=style.noop_stylist):
    # load additional files
    logger.info("Looking for additional files to run")
    additional_files = settings.ADDITIONAL_SCHEMA_FILE
    for file_name in additional_files:
        if not file_name:
            continue
        file_path = os.path.join(settings.MIGRATIONS_ROOT, "schemas", file_name)
        logger.info("Loading %s", file_path)
        run_script(file_path)

    # load schema
    with stylist.activate("title") as echo:
        echo("Loading schema")

    schema_path = os.path.join(
        settings.MIGRATIONS_ROOT,
        "schemas",
        settings.SCHEMA_TEMPLATE.format(init_version),
    )
    logger.info("Loading %s", schema_path)

    with stylist.checkbox(
        content="Applying {}...".format(init_version),
        content_after="Applied {}".format(init_version),
    ):

        run_script(schema_path)

    create_fake_entries(init_version)

    # load fixtures
    try:
        fixtures_version = core.get_fixtures_version(init_version)
        fixtures_path = os.path.join(
            settings.MIGRATIONS_ROOT,
            "fixtures",
            settings.FIXTURES_TEMPLATE.format(fixtures_version),
        )
        with stylist.activate("title") as echo:
            echo("Loading fixtures")
        logger.info("Applying fixture %s (file %s)", fixtures_version, fixtures_path)
        with stylist.checkbox(
            content="Applying fixtures {}...".format(fixtures_version),
            content_after="Applied fixtures {}".format(fixtures_version),
        ):
            run_script(fixtures_path)
    except exceptions.SeptentrionException as exception:
        logger.info("Not applying fixtures: %s", exception)


def create_fake_entries(version, stylist=style.noop_stylist):
    """
    Write entries in the migration table for all existing migrations
    up until the given version (included).
    """
    # Fake migrations <= init_version
    known_versions = files.get_known_versions()
    versions_to_fake = list(utils.until(known_versions, version))
    logger.info("Will now fake all migrations up to version %s (included)", version)

    with stylist.activate("title") as echo:
        echo("Faking migrations.")

    for version in versions_to_fake:
        logger.info("Faking migrations from version %s", version)
        migrations_to_apply = files.get_migrations_files_mapping(version)
        migs = list(migrations_to_apply)
        migs.sort()
        for migration_name in migs:
            logger.info("Faking %s", migration_name)
            with stylist.checkbox(
                content="Faking {}...".format(migration_name),
                content_after="Faked {}".format(migration_name),
            ):
                db.write_migration(version, migration_name)


def run_script(path):
    logger.info("Running SQL file %s", path)
    with io.open(path, "r", encoding="utf8") as f:
        script = runner.Script(f)
        script.run(db.get_connection())
