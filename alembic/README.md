# Alembic Migrations

This directory contains database migrations for the project using Alembic.

## Usage

### Creating a New Migration

To create a new migration, run:

```bash
# Generate a migration automatically by comparing the database to your models
alembic revision --autogenerate -m "Description of the changes"

# Or create an empty migration
alembic revision -m "Description of the changes"
```

### Applying Migrations

To apply all pending migrations:

```bash
alembic upgrade head
```

To apply migrations up to a specific revision:

```bash
alembic upgrade <revision_id>
```

### Rolling Back Migrations

To roll back the most recent migration:

```bash
alembic downgrade -1
```

To roll back to a specific revision:

```bash
alembic downgrade <revision_id>
```

### Viewing Migration History

To see the migration history:

```bash
alembic history
```

### Viewing Current Database Version

To see the current database version:

```bash
alembic current
```

## Migration Files

Migration files are stored in the `versions` directory. Each file contains:

- `upgrade()` function: Code to apply the migration
- `downgrade()` function: Code to roll back the migration

## Configuration

The Alembic configuration is in `alembic.ini` in the project root directory.
The database connection is configured using the project's settings.
