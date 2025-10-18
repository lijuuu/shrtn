#!/bin/bash

# PostgreSQL initialization script
# This script sets up the PostgreSQL database based on environment variables

set -e

echo "Starting PostgreSQL initialization..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h localhost -p 5432 -U "${POSTGRES_USER:-postgres}"; do
    echo "PostgreSQL is not ready yet. Waiting..."
    sleep 2
done

echo "PostgreSQL is ready. Setting up database..."

# Create database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-postgres}" --dbname "postgres" <<-EOSQL
    SELECT 'CREATE DATABASE ${POSTGRES_DB:-hirethon_template}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB:-hirethon_template}')\gexec
EOSQL

echo "Database '${POSTGRES_DB:-hirethon_template}' created successfully."

# Create extensions and perform additional setup
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-postgres}" --dbname "${POSTGRES_DB:-hirethon_template}" <<-EOSQL
    -- Create extensions if needed
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "btree_gin";
    
    -- Create custom types if needed
    -- CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
    -- CREATE TYPE organization_role AS ENUM ('owner', 'admin', 'member', 'viewer');
    
    -- Grant permissions to the database user
    GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB:-hirethon_template} TO ${POSTGRES_USER:-postgres};
    GRANT ALL PRIVILEGES ON SCHEMA public TO ${POSTGRES_USER:-postgres};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER:-postgres};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${POSTGRES_USER:-postgres};
    
    -- Set default privileges for future objects
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${POSTGRES_USER:-postgres};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${POSTGRES_USER:-postgres};
EOSQL

echo "PostgreSQL initialization completed successfully!"
