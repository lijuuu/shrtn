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

-- Create simple analytics table for URL tracking
CREATE TABLE IF NOT EXISTS url_analytics (
    namespace_id INT,
    shortcode TEXT,
    lookup_date DATE,
    lookup_timestamp TIMESTAMP,
    country TEXT,
    ip_address TEXT,
    user_agent TEXT,
    referer TEXT,
    PRIMARY KEY ((namespace_id, shortcode), lookup_date, lookup_timestamp)
) WITH CLUSTERING ORDER BY (lookup_date DESC, lookup_timestamp DESC)
AND compression = {'sstable_compression': 'LZ4Compressor'};

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_url_analytics_country ON url_analytics (country);
CREATE INDEX IF NOT EXISTS idx_url_analytics_date ON url_analytics (lookup_date);

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
