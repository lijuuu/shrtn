#!/bin/bash

# Wait for database to be ready
echo "Waiting for databases to be ready..."

# Determine if we're running inside Docker or on host
if [ -f /.dockerenv ]; then
    # Inside Docker container
    POSTGRES_HOST="postgres"
    SCYLLA_HOST="scylla"
    REDIS_HOST="redis"
else
    # On host machine
    POSTGRES_HOST="localhost"
    SCYLLA_HOST="localhost"
    REDIS_HOST="localhost"
fi

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z $POSTGRES_HOST 5432; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for ScyllaDB
echo "Waiting for ScyllaDB..."
while ! nc -z $SCYLLA_HOST 9042; do
  sleep 1
done
echo "ScyllaDB is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z $REDIS_HOST 6379; do
  sleep 1
done
echo "Redis is ready!"

echo "All databases are ready!"
