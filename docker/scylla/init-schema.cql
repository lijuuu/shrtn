-- ScyllaDB schema initialization script
-- This script runs when the ScyllaDB container starts

-- Create keyspace with proper configuration
CREATE KEYSPACE IF NOT EXISTS hirethon_keyspace 
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

-- Use the keyspace
USE hirethon_keyspace;

-- Create short_urls table with proper sharding
CREATE TABLE IF NOT EXISTS short_urls (
    namespace_id INT,
    shortcode TEXT,
    id UUID,
    created_at TIMESTAMP,
    created_by_user_id INT,
    original_url TEXT,
    expiry TIMESTAMP,
    click_count INT,
    updated_at TIMESTAMP,
    is_private BOOLEAN,
    tags SET<TEXT>,
    PRIMARY KEY ((namespace_id, shortcode), id, created_at)
) WITH CLUSTERING ORDER BY (id ASC, created_at DESC);

-- Create click analytics table
CREATE TABLE IF NOT EXISTS click_analytics (
    namespace_id INT,
    shortcode TEXT,
    click_date DATE,
    click_timestamp TIMESTAMP,
    user_agent TEXT,
    ip_address TEXT,
    referer TEXT,
    country TEXT,
    city TEXT,
    PRIMARY KEY ((namespace_id, shortcode), click_date, click_timestamp)
) WITH CLUSTERING ORDER BY (click_date DESC, click_timestamp DESC);

-- Create bulk upload mappings table
CREATE TABLE IF NOT EXISTS bulk_upload_mappings (
    bulk_upload_id INT,
    shortcode TEXT,
    original_url TEXT,
    status TEXT,
    created_at TIMESTAMP,
    processed_at TIMESTAMP,
    error_message TEXT,
    PRIMARY KEY (bulk_upload_id, shortcode)
);

-- Create namespace statistics table
CREATE TABLE IF NOT EXISTS namespace_stats (
    namespace_id INT,
    total_urls INT,
    total_clicks INT,
    active_urls INT,
    expired_urls INT,
    last_updated TIMESTAMP,
    PRIMARY KEY (namespace_id)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_short_urls_created_by ON short_urls (created_by_user_id);
CREATE INDEX IF NOT EXISTS idx_short_urls_expiry ON short_urls (expiry);
CREATE INDEX IF NOT EXISTS idx_short_urls_is_private ON short_urls (is_private);
