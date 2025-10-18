#!/bin/bash

# Custom ScyllaDB entrypoint that runs ScyllaDB and then initialization

set -e

# Start ScyllaDB in the background
echo "Starting ScyllaDB..."
scylla --smp 1 --memory 750M --overprovisioned  &

# Wait for ScyllaDB to be ready and run initialization
echo "Waiting for ScyllaDB to be ready..."
sleep 30

# Run our initialization script
if [ -f "/init-scylla.sh" ]; then
    echo "Running ScyllaDB initialization..."
    /init-scylla.sh
fi

# Keep the container running
wait
