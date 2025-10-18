#!/bin/bash

# Custom ScyllaDB entrypoint that runs ScyllaDB and then our setup script

set -e

# Start ScyllaDB in the background with 3 shards
echo "Starting ScyllaDB with 3 shards..."
scylla --seeds=scylla --smp 1 --memory 750M --overprovisioned 1 --num-tokens=3 --vnodes=3 &

# Wait for ScyllaDB to be ready
echo "Waiting for ScyllaDB to be ready..."
sleep 10

# Run our setup script
if [ -f "/docker-entrypoint-initdb.d/setup.sh" ]; then
    echo "Running ScyllaDB setup script..."
    /docker-entrypoint-initdb.d/setup.sh
fi

# Keep the container running
wait
