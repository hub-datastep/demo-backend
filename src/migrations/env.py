import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

load_dotenv()
config.set_main_option('sqlalchemy.url', os.getenv("DB_CONNECTION_STRING"))

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel

# noinspection PyTypeChecker
from scheme.chat.chat_scheme import Chat
from scheme.prediction.database_prediction_config_scheme import DatabasePredictionConfig
from scheme.file.file_scheme import File
from scheme.chat.mark_scheme import Mark
from scheme.chat.message_scheme import Message
from scheme.mode.mode_scheme import Mode
from scheme.mode.mode_tenant_scheme import ModeTenantLink
from scheme.prompt.prompt_scheme import Prompt
from scheme.chat.review_scheme import Review
from scheme.tenant.tenant_scheme import Tenant
from scheme.auth.token_scheme import Token
from scheme.user.user_scheme import User
from scheme.user.user_tenant_scheme import UserTenantLink
from scheme.classifier.classifier_version_scheme import ClassifierVersion
from scheme.classifier.classifier_config_scheme import ClassifierConfig
from scheme.mapping.mapping_results_scheme import MappingResult
from scheme.used_token.used_token_scheme import UsedToken

# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
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
    url = config.get_main_option("sqlalchemy.url")
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
        config.get_section(config.config_ini_section, {}),
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
