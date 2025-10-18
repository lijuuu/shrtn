#!/bin/bash

# ScyllaDB Initialization Script
# This script waits for ScyllaDB to be ready and then runs the CQL files

set -e

echo "Starting ScyllaDB initialization..."

# Wait for ScyllaDB to be ready
echo "Waiting for ScyllaDB to be ready..."
until cqlsh -e "DESCRIBE KEYSPACES;" > /dev/null 2>&1; do
    echo "ScyllaDB is not ready yet. Waiting..."
    sleep 5
done

echo "ScyllaDB is ready. Running initialization scripts..."

# Run the keyspace initialization
if [ -f "/docker-entrypoint-initdb.d/01-init-keyspace.cql" ]; then
    echo "Creating keyspace..."
    cqlsh -f /docker-entrypoint-initdb.d/01-init-keyspace.cql
    echo "Keyspace created successfully."
fi

# Run the tables creation
if [ -f "/docker-entrypoint-initdb.d/02-create-tables.cql" ]; then
    echo "Creating tables..."
    cqlsh -f /docker-entrypoint-initdb.d/02-create-tables.cql
    echo "Tables created successfully."
fi

echo "ScyllaDB initialization completed successfully!"
