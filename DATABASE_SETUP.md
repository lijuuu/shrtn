# Database Setup Guide

This document describes the automated database setup for the Hirethon Django Template.

## Overview

The project uses two databases:
- **PostgreSQL**: For Django models and relational data
- **ScyllaDB**: For high-performance NoSQL operations (URL shortener)

## Automated Setup

The database setup is fully automated through Docker Compose and initialization scripts.

### Quick Start

```bash
# Start all services with automated database setup
./start.sh
```

### Manual Setup

```bash
# Build and start services
docker-compose -f local.yml up --build -d

# Check service status
docker-compose -f local.yml ps

# View logs
docker-compose -f local.yml logs -f
```

## Environment Configuration

### ScyllaDB Configuration (`.envs/.local/.scylla`)

```bash
# ScyllaDB Configuration
SCYLLA_HOSTS=127.0.0.1:9042
SCYLLA_KEYSPACE=hirethon_keyspace
SCYLLA_DATACENTER=datacenter1
SCYLLA_REPLICATION_FACTOR=1

# Sharding Strategy
SCYLLA_PARTITION_KEY_STRATEGY=composite
SCYLLA_PARTITION_KEY_FIELDS=namespace_id,shortcode
SCYLLA_CLUSTERING_KEY_FIELDS=id,created_at
SCYLLA_CONSISTENCY_LEVEL=LOCAL_ONE
SCYLLA_COMPRESSION=true

# Shard Configuration
SCYLLA_VNODES=2
SCYLLA_SHARD_COUNT=2
```

### PostgreSQL Configuration (`.envs/.local/.postgres`)

```bash
# PostgreSQL Configuration
POSTGRES_DB=hirethon_template
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Database URL for Django
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/hirethon_template
```

## Database Initialization

### ScyllaDB Setup

The ScyllaDB initialization script (`compose/local/scylla/init/setup.sh`) automatically:

1. Waits for ScyllaDB to be ready
2. Creates the keyspace with the configured replication factor
3. Creates all necessary tables with proper partitioning and clustering
4. Sets up indexes for optimal query performance
5. Configures compression and consistency levels

### PostgreSQL Setup

The PostgreSQL initialization script (`compose/local/postgres/init/setup.sh`) automatically:

1. Waits for PostgreSQL to be ready
2. Creates the database if it doesn't exist
3. Installs required extensions (uuid-ossp, pg_trgm, btree_gin)
4. Sets up proper permissions for the database user
5. Configures default privileges for future objects

## Service Ports

- **Django App**: http://localhost:8000
- **PostgreSQL**: localhost:5433
- **ScyllaDB**: localhost:9042
- **Redis**: localhost:6379
- **Flower (Celery)**: http://localhost:5555

## Troubleshooting

### Check Service Status

```bash
docker-compose -f local.yml ps
```

### View Logs

```bash
# All services
docker-compose -f local.yml logs -f

# Specific service
docker-compose -f local.yml logs -f scylla
docker-compose -f local.yml logs -f postgres
```

### Reset Databases

```bash
# Stop and remove all containers and volumes
docker-compose -f local.yml down -v

# Start fresh
./start.sh
```

### Manual Database Access

#### ScyllaDB

```bash
# Connect to ScyllaDB
docker exec -it hirethon_template_local_scylla cqlsh

# List keyspaces
DESCRIBE KEYSPACES;

# Use the keyspace
USE hirethon_keyspace;

# List tables
DESCRIBE TABLES;
```

#### PostgreSQL

```bash
# Connect to PostgreSQL
docker exec -it hirethon_template_local_postgres psql -U postgres -d hirethon_template

# List databases
\l

# List tables
\dt
```

## Development Notes

- The setup scripts run automatically when containers start
- Environment variables are loaded from `.envs/.local/` directory
- All database schemas are created automatically - no manual Django migrations needed for initial setup
- The system is designed to be completely self-contained and reproducible
