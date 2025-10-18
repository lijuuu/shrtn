-- Simple analytics schema for short URL tracking
-- Single table for all analytics data

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

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_url_analytics_country ON url_analytics (country);
CREATE INDEX IF NOT EXISTS idx_url_analytics_date ON url_analytics (lookup_date);
