FROM scylladb/scylla:latest

# Create a custom entrypoint that runs our setup script
COPY ./compose/local/scylla/init/setup.sh /docker-entrypoint-initdb.d/setup.sh
RUN chmod +x /docker-entrypoint-initdb.d/setup.sh

# Create a custom entrypoint script that runs ScyllaDB and then our setup
COPY ./compose/local/scylla/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
