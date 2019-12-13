import attr
import pathlib
from typing import Iterable


@attr.dataclass
class Migration:
    version: str
    name: str

    @property
    def path(self) -> pathlib.Path:
        return pathlib.Path(self.version) / self.name


@attr.dataclass
class Operation:
    pass


class ApplySchema(Operation):
    version: str
    path: str


class Migrate(Operation):
    migration: Migration
    fake: bool = False


class AlreadyApplied(Operation):
    migration: Migration


def build_migration_plan(
    file_migrations, database_versions, target_version
) -> Iterable[Operation]:
    """
    Yields a list of migration operations to do.
    Initialization steps are not included.
    This function doesn't execute any migration, but lists them.
    """
    # get all versions to apply
    try:
        versions_to_apply = list(utils.until(known_versions, target_version))
    except ValueError:
        raise ValueError(
            "settings.TARGET_VERSION is improperly configured: "
            "version {} not found.".format(settings.TARGET_VERSION)
        )

    # get plan for each version to apply
    for version in versions_to_apply:
        version_plan = []
        # get applied migrations
        applied_migrations = db.get_applied_migrations(
            settings=settings, version=version
        )
        # get migrations to apply
        migrations_to_apply = files.get_migrations_files_mapping(
            settings=settings, version=version
        )
        migs = list(migrations_to_apply)
        migs.sort()
        # build plan
        for mig in migs:
            applied = mig in applied_migrations
            path = migrations_to_apply[mig]
            is_manual = files.is_manual_migration(os.path.abspath(path))
            version_plan.append((mig, applied, path, is_manual))
            yield {"version": version, "plan": version_plan}
