# -*- coding: utf-8 -*-
import io
import logging
import os.path

from west import core
from west import db
from west import exceptions
from west import files
from west import runner
from west import utils
from west.settings import settings

logger = logging.getLogger(__name__)


def migrate():

    if not db.is_schema_initialized():
        # schema not inited
        schema_version = core.get_best_schema_version()
        init_schema(schema_version)

    # play migrations
    print("Apply migrations")
    for plan in core.build_migration_plan():
        version = plan["version"]
        logger.info(version)
        for mig, applied, path, is_manual in plan["plan"]:
            title = mig
            if is_manual:
                title += " (manual)"
            if applied:
                print("  {} already applied".format(title))
            else:
                print("  Applying {}...".format(title))
                run_script(path)
                db.write_migration(version, mig)


def init_schema(init_version):
    # load additional files
    additional_files = settings.ADDITIONAL_SCHEMA_FILE
    for file_name in additional_files:
        if not file_name:
            continue
        file_path = os.path.join(settings.MIGRATIONS_ROOT, "schemas", file_name)
        logger.info("Load {}".format(file_name))
        run_script(file_path)

    # load schema
    print("Load schema")
    print("  Applying {}...".format(init_version))
    schema_path = os.path.join(
        settings.MIGRATIONS_ROOT,
        "schemas",
        settings.SCHEMA_TEMPLATE.format(init_version),
    )
    run_script(schema_path)

    # Fake migrations <= init_version
    known_versions = files.get_known_versions()
    versions_to_fake = list(utils.until(known_versions, init_version))
    for version in versions_to_fake:
        migrations_to_apply = files.get_migrations_files_mapping(version)
        migs = list(migrations_to_apply)
        migs.sort()
        for migration_name in migs:
            db.write_migration(version, migration_name)
            print("Faking {}...".format(migration_name))

    # load fixtures
    try:
        fixtures_version = core.get_fixtures_version(init_version)
        fixtures_path = os.path.join(
            settings.MIGRATIONS_ROOT,
            "fixtures",
            settings.FIXTURES_TEMPLATE.format(fixtures_version),
        )
        print("Load fixtures")
        print("  Applying {}...".format(fixtures_version))
        run_script(fixtures_path)
    except exceptions.WestException:
        pass


def run_script(path):
    with io.open(path, "r", encoding="utf8") as f:
        script = runner.Script(f)
        script.run(db.get_connection())
