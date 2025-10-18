-- ScyllaDB Keyspace Initialization
-- This script creates the keyspace with environment variables

CREATE KEYSPACE IF NOT EXISTS ${SCYLLA_KEYSPACE}
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': ${SCYLLA_REPLICATION_FACTOR}
};

-- Use the keyspace
USE ${SCYLLA_KEYSPACE};
