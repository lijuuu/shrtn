-- PostgreSQL Extensions Setup
-- This script creates necessary extensions for the application

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Grant usage on extensions to the application user
GRANT USAGE ON SCHEMA public TO ${POSTGRES_USER};
