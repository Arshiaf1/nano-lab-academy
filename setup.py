#!/usr/bin/env python
"""Setup script to initialize the FastAPI backend project."""

import os
import subprocess
import sys
from pathlib import Path

def create_directory_structure():
    """Create the necessary directory structure."""
    base_dir = Path(__file__).parent
    
    # Create alembic directories
    alembic_dir = base_dir / "alembic"
    alembic_dir.mkdir(exist_ok=True)
    
    versions_dir = alembic_dir / "versions"
    versions_dir.mkdir(exist_ok=True)
    
    # Create __init__.py files
    (alembic_dir / "__init__.py").touch()
    (versions_dir / "__init__.py").touch()
    
    # Create env.py
    env_py = alembic_dir / "env.py"
    if not env_py.exists():
        env_content = '''"""Alembic configuration file for async database migrations."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = "sqlite+aiosqlite:///./nano_lab.db"

    context.configure(
        url=configuration["sqlalchemy.url"],
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_async_migrations(connection):
    """Run migrations with asyncio."""
    ctx = context.MigrationContext.configure(connection)

    with ctx.begin_transaction():
        ctx.run_migrations()


async def run_async_migrations():
    """Create an engine and run migrations"""
    connectable = create_async_engine(
        "sqlite+aiosqlite:///./nano_lab.db",
        future=True,
        echo=True,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_async_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        env_py.write_text(env_content)
    
    print("✓ Directory structure created")
    print("✓ Alembic env.py created")

def main():
    """Main setup function."""
    print("Setting up FastAPI backend project...")
    create_directory_structure()
    print("✓ Setup complete!")

if __name__ == "__main__":
    main()
