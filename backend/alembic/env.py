import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al path (para que funcione en Docker y local)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# Config Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# IMPORTA TU CONFIG Y MODELOS
from app.config import settings
from app.infrastructure.database.base import Base
from app.infrastructure.database import models  # noqa: F401  (asegura que se registren)

target_metadata = Base.metadata


def get_url() -> str:
    # Usa exactamente la misma URL que tu app (lee de .env o Docker)
    return settings.database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        connectable = create_engine(get_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations() -> None:
    """Entry point for Alembic."""
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


run_migrations()