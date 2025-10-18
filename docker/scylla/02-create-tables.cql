-- ScyllaDB Tables Creation
-- This script creates all necessary tables for the application

-- Use the keyspace
USE ${SCYLLA_KEYSPACE};

-- Create short_urls table with composite partition key
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
) WITH CLUSTERING ORDER BY (id ASC, created_at DESC)
AND compression = {'sstable_compression': 'LZ4Compressor'};

-- Create an index for looking up by created_by_user_id
CREATE INDEX IF NOT EXISTS idx_short_urls_created_by ON short_urls (created_by_user_id);

-- Create an index for looking up by expiry (for cleanup jobs)
CREATE INDEX IF NOT EXISTS idx_short_urls_expiry ON short_urls (expiry);

-- Create an index for looking up by is_private
CREATE INDEX IF NOT EXISTS idx_short_urls_is_private ON short_urls (is_private);

-- Create a table for tracking click analytics
CREATE TABLE IF NOT EXISTS click_analytics (
    shortcode TEXT,
    namespace_id INT,
    click_date DATE,
    click_timestamp TIMESTAMP,
    user_agent TEXT,
    ip_address TEXT,
    referer TEXT,
    country TEXT,
    city TEXT,
    PRIMARY KEY ((shortcode, namespace_id), click_date, click_timestamp)
) WITH CLUSTERING ORDER BY (click_date DESC, click_timestamp DESC)
AND compression = {'sstable_compression': 'LZ4Compressor'};

-- Create a table for bulk upload tracking
CREATE TABLE IF NOT EXISTS bulk_upload_mappings (
    bulk_upload_id INT,
    shortcode TEXT,
    original_url TEXT,
    status TEXT, -- 'pending', 'processed', 'failed'
    created_at TIMESTAMP,
    processed_at TIMESTAMP,
    error_message TEXT,
    PRIMARY KEY (bulk_upload_id, shortcode)
) WITH compression = {'sstable_compression': 'LZ4Compressor'};

-- Create a table for namespace statistics
CREATE TABLE IF NOT EXISTS namespace_stats (
    namespace_id INT,
    total_urls INT,
    total_clicks INT,
    active_urls INT,
    expired_urls INT,
    last_updated TIMESTAMP,
    PRIMARY KEY (namespace_id)
) WITH compression = {'sstable_compression': 'LZ4Compressor'};
