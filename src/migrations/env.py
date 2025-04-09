from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from infra.env import env

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url",
    env.DB_CONNECTION_STRING,
)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel

# noinspection PyUnresolvedReferences
from scheme.chat.chat_scheme import Chat
# noinspection PyUnresolvedReferences
from scheme.prediction.database_prediction_config_scheme import DatabasePredictionConfig
# noinspection PyUnresolvedReferences
from scheme.file.file_scheme import File
# noinspection PyUnresolvedReferences
from scheme.chat.mark_scheme import Mark
# noinspection PyUnresolvedReferences
from scheme.chat.message_scheme import Message
# noinspection PyUnresolvedReferences
from scheme.mode.mode_scheme import Mode
# noinspection PyUnresolvedReferences
from scheme.mode.mode_tenant_scheme import ModeTenantLink
# noinspection PyUnresolvedReferences
from scheme.prompt.prompt_scheme import Prompt
# noinspection PyUnresolvedReferences
from scheme.chat.review_scheme import Review
# noinspection PyUnresolvedReferences
from scheme.tenant.tenant_scheme import Tenant
# noinspection PyUnresolvedReferences
from scheme.auth.token_scheme import Token
# noinspection PyUnresolvedReferences
from scheme.user.user_scheme import User
# noinspection PyUnresolvedReferences
from scheme.classifier.classifier_version_scheme import ClassifierVersion
# noinspection PyUnresolvedReferences
from scheme.classifier.classifier_config_scheme import ClassifierConfig
# noinspection PyUnresolvedReferences
from scheme.mapping.result.mapping_result_scheme import MappingResult
# noinspection PyUnresolvedReferences
from scheme.mapping.result.mapping_iteration_scheme import MappingIteration
# noinspection PyUnresolvedReferences
from scheme.used_token.used_token_scheme import UsedToken
# noinspection PyUnresolvedReferences
from scheme.role.role_scheme import Role
# noinspection PyUnresolvedReferences
from scheme.order_classification.order_classification_config_scheme import OrderClassificationConfig
# noinspection PyUnresolvedReferences
from scheme.solution_imitation.solution_imitation_config_scheme import SolutionImitationConfig
# noinspection PyUnresolvedReferences
from scheme.order_tracking.order_tracking_task_scheme import OrderTrackingTask

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
