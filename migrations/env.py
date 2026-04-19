"""Alembic environment configuration."""

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides access to the values within the .ini file
config = context.config

fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline():
    raise NotImplementedError


def run_migrations_online():
    raise NotImplementedError


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
