#!/bin/bash

# PostgreSQL Database and User Initialization Script
# This script creates the database and user from environment variables

set -e

echo "Starting PostgreSQL initialization..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h localhost -p 5432 -U postgres; do
    echo "PostgreSQL is not ready yet. Waiting..."
    sleep 2
done

echo "PostgreSQL is ready. Setting up database and user..."

# Create the database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username postgres --dbname postgres <<-EOSQL
    SELECT 'CREATE DATABASE ${POSTGRES_DB}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}')\gexec
EOSQL

echo "Database '${POSTGRES_DB}' created successfully."

# Create the user if it doesn't exist and grant privileges
psql -v ON_ERROR_STOP=1 --username postgres --dbname postgres <<-EOSQL
    DO \$\$
    BEGIN
       IF NOT EXISTS (
          SELECT FROM pg_catalog.pg_roles
          WHERE  rolname = '${POSTGRES_USER}') THEN

          CREATE ROLE ${POSTGRES_USER} LOGIN PASSWORD '${POSTGRES_PASSWORD}';
       END IF;
    END
    \$\$;

    GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};
EOSQL

echo "User '${POSTGRES_USER}' created successfully."

# Connect to the target database and set up schema privileges
psql -v ON_ERROR_STOP=1 --username postgres --dbname ${POSTGRES_DB} <<-EOSQL
    GRANT ALL ON SCHEMA public TO ${POSTGRES_USER};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${POSTGRES_USER};
    
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${POSTGRES_USER};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${POSTGRES_USER};
EOSQL

echo "Schema privileges granted successfully."

# Create extensions
psql -v ON_ERROR_STOP=1 --username postgres --dbname ${POSTGRES_DB} <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "btree_gin";
    CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
    
    GRANT USAGE ON SCHEMA public TO ${POSTGRES_USER};
EOSQL

echo "Extensions created successfully."
echo "PostgreSQL initialization completed successfully!"
