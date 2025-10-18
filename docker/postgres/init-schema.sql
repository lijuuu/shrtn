-- PostgreSQL schema initialization script
-- This script runs when the PostgreSQL container starts

-- Create the database if it doesn't exist (this is handled by POSTGRES_DB env var)
-- But we can add any additional setup here

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types if needed
-- CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
-- CREATE TYPE organization_role AS ENUM ('owner', 'admin', 'member', 'viewer');

-- The actual tables will be created by Django migrations
-- This file is here for any custom PostgreSQL setup that needs to happen
-- before Django migrations run
