-- ScyllaDB Tables Creation
-- This script creates all necessary tables for the application

-- Use the keyspace
USE ${SCYLLA_KEYSPACE};

-- Create short_urls table with composite partition key
CREATE TABLE IF NOT EXISTS short_urls (
    namespace_id UUID,
    shortcode TEXT,
    id UUID,
    created_at TIMESTAMP,
    created_by_user_id UUID,
    original_url TEXT,
    title TEXT,
    description TEXT,
    expiry TIMESTAMP,
    click_count INT,
    updated_at TIMESTAMP,
    is_private BOOLEAN,
    is_active BOOLEAN,
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
    namespace_id UUID,
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

