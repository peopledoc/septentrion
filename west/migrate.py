# -*- coding: utf-8 -*-
import io
import logging
import os.path

from west import db
from west import exceptions
from west import west
from west import runner
from west.settings import settings

logger = logging.getLogger(__name__)


def migrate():
    # build miration plan
    migration_plan = west.build_migration_plan()

    if migration_plan is None:
        # schema not inited
        init_schema()
        # reload migration_plan
        migration_plan = west.build_migration_plan()

    # play migrations
    for plan in migration_plan['plans']:
        version = plan['version']
        logger.info(version)
        for mig, applied, path, is_manual in plan['plan']:
            title = mig
            if is_manual:
                title += ' (manual)'
            if applied:
                logger.info("  {} already applied".format(title))
            else:
                logger.info("  Applying {}...".format(title))
                run_script(path)
                db.write_migration(version, mig)


def init_schema():
    init_version = west.get_schema_version()

    # load additional files
    additional_files = settings.ADDITIONAL_SCHEMA_FILES or ''
    for file_name in additional_files.split(","):
        if not file_name:
            continue
        file_path = os.path.join(
            settings.MIGRATIONS_ROOT, 'schemas', file_name)
        logger.info("Load {}".format(file_name))
        run_script(file_path)

    # load schema
    logger.info("Load schema")
    logger.info("  Applying %s...", init_version)
    schema_path = os.path.join(
        settings.MIGRATIONS_ROOT,
        'schemas',
        settings.SCHEMA_TEMPLATE.format(init_version))
    run_script(schema_path)

    # load fixtures
    try:
        fixtures_version = west.get_fixtures_version(init_version)
        fixtures_path = os.path.join(
            settings.MIGRATIONS_ROOT,
            'fixtures',
            settings.FIXTURES_TEMPLATE.format(fixtures_version))
        logger.info("Load fixtures")
        logger.info("  Applying %s...", fixtures_version)
        run_script(fixtures_path)
    except exceptions.WestException:
        pass


def run_script(path):
    with io.open(path, 'r', encoding='utf8') as f:
        script = runner.Script(f)
        script.run(db.get_connection())
