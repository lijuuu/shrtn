#!/usr/bin/env python3
"""
Simple test script for ScyllaDB connection without Django dependencies.
"""
import os
import sys
import asyncio
import uuid
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.insert(0, '/home/xstill/Hackathon/hirethon-django-template')

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
os.environ.setdefault('USE_DOCKER', 'no')
os.environ.setdefault('SCYLLA_HOSTS', '127.0.0.1:9042')
os.environ.setdefault('SCYLLA_KEYSPACE', 'hirethon_keyspace')
os.environ.setdefault('SCYLLA_TABLE', 'short_urls')

import acsylla

async def test_scylla_connection():
    """Test basic ScyllaDB connection and operations."""
    print("🔗 Testing ScyllaDB connection...")
    
    try:
        # Connect to ScyllaDB
        hosts = ['127.0.0.1']
        cluster = acsylla.create_cluster(hosts)
        session = await cluster.create_session(keyspace='hirethon_keyspace')
        
        print("✅ Connected to ScyllaDB successfully!")
        
        # Test 1: Create a short URL
        print("\n📝 Test 1: Creating short URL...")
        url_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        
        query = """
        INSERT INTO short_urls (
            namespace_id, shortcode, id, created_at, created_by_user_id,
            original_url, expiry, click_count, updated_at, is_private, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        prepared = await session.create_prepared(query)
        statement = prepared.bind()
        statement.bind(0, 1)  # namespace_id
        statement.bind(1, 'test123')  # shortcode
        statement.bind(2, url_id)  # id
        statement.bind(3, now)  # created_at
        statement.bind(4, 1)  # created_by_user_id
        statement.bind(5, 'https://example.com/test')  # original_url
        statement.bind(6, None)  # expiry
        statement.bind(7, 0)  # click_count
        statement.bind(8, now)  # updated_at
        statement.bind(9, False)  # is_private
        statement.bind(10, {'test', 'demo'})  # tags
        
        await session.execute(statement)
        print("✅ Short URL created successfully!")
        
        # Test 2: Retrieve the short URL
        print("\n🔍 Test 2: Retrieving short URL...")
        get_query = """
        SELECT * FROM short_urls
        WHERE namespace_id = ? AND shortcode = ?
        LIMIT 1
        """
        
        get_prepared = await session.create_prepared(get_query)
        get_statement = get_prepared.bind()
        get_statement.bind(0, 1)  # namespace_id
        get_statement.bind(1, 'test123')  # shortcode
        
        result = await session.execute(get_statement)
        rows = list(result)
        
        if rows:
            row = rows[0]
            print(f"✅ Retrieved: {row.shortcode} -> {row.original_url}")
            print(f"   Click count: {row.click_count}")
            print(f"   Tags: {list(row.tags) if row.tags else []}")
        else:
            print("❌ Failed to retrieve short URL")
        
        # Test 3: Increment click count
        print("\n📈 Test 3: Incrementing click count...")
        update_query = """
        UPDATE short_urls
        SET click_count = click_count + 1, updated_at = ?
        WHERE namespace_id = ? AND shortcode = ?
        """
        
        update_prepared = await session.create_prepared(update_query)
        update_statement = update_prepared.bind()
        update_statement.bind(0, datetime.now(timezone.utc))  # updated_at
        update_statement.bind(1, 1)  # namespace_id
        update_statement.bind(2, 'test123')  # shortcode
        
        await session.execute(update_statement)
        print("✅ Click count incremented!")
        
        # Verify click count
        result = await session.execute(get_statement)
        rows = list(result)
        if rows:
            row = rows[0]
            print(f"✅ Click count is now: {row.click_count}")
        
        # Test 4: Delete the short URL
        print("\n🗑️  Test 4: Deleting short URL...")
        delete_query = """
        DELETE FROM short_urls
        WHERE namespace_id = ? AND shortcode = ?
        """
        
        delete_prepared = await session.create_prepared(delete_query)
        delete_statement = delete_prepared.bind()
        delete_statement.bind(0, 1)  # namespace_id
        delete_statement.bind(1, 'test123')  # shortcode
        
        await session.execute(delete_statement)
        print("✅ Short URL deleted!")
        
        # Verify deletion
        result = await session.execute(get_statement)
        rows = list(result)
        if not rows:
            print("✅ Deletion verified!")
        else:
            print("❌ URL still exists after deletion")
        
        # Close connection
        await cluster.close()
        print("\n🎉 All ScyllaDB tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scylla_connection())
