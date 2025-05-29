import sys

sys.path.insert(0, ".")

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from project.domains.base.models import public_schema
from project.settings import Settings

import importlib
from pathlib import Path

project_root = Path(__file__).parent.parent
domains_path = project_root / "project" / "domains"

for py_file in domains_path.rglob("*.py"):
    rel_path = py_file.relative_to(project_root)
    module_parts = list(rel_path.parts)
    module_parts[-1] = module_parts[-1][:-3]  # Remove .py extension
    module_path = ".".join(module_parts)
    importlib.import_module(module_path)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# Set the SQLAlchemy URL from project settings
context.config.set_main_option("sqlalchemy.url", str(Settings().SQLALCHEMY_DATABASE_DSN))

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = public_schema


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = context.config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = context.config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
