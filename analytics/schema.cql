-- Simple analytics schema for short URL tracking
-- Single table for all analytics data

CREATE TABLE IF NOT EXISTS click_analytics (
    namespace_id INT,
    shortcode TEXT,
    click_date DATE,
    click_timestamp TIMESTAMP,
    country TEXT,
    ip_address TEXT,
    user_agent TEXT,
    referer TEXT,
    PRIMARY KEY ((namespace_id, shortcode), click_date, click_timestamp)
) WITH CLUSTERING ORDER BY (click_date DESC, click_timestamp DESC)
AND compression = {'sstable_compression': 'LZ4Compressor'};

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_click_analytics_country ON click_analytics (country);
CREATE INDEX IF NOT EXISTS idx_click_analytics_date ON click_analytics (click_date);
