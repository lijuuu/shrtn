#!/usr/bin/env python3
"""
Simple test script for ScyllaDB connection using acsylla with proper error handling.
"""
import os
import sys
import asyncio
import uuid
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.insert(0, '/home/xstill/Hackathon/hirethon-django-template')

import acsylla

async def test_scylla_connection():
    """Test basic ScyllaDB connection and operations."""
    print("🔗 Testing ScyllaDB connection...")
    
    try:
        # Connect to ScyllaDB
        hosts = ['localhost']
        print(f"Connecting to hosts: {hosts}")
        
        cluster = acsylla.create_cluster(hosts)
        print("Cluster created")
        
        session = await cluster.create_session(keyspace='hirethon_keyspace')
        print("Session created with keyspace")
        
        print("✅ Connected to ScyllaDB successfully!")
        
        # Test 1: Simple query first
        print("\n📝 Test 1: Simple query...")
        simple_query = "SELECT * FROM short_urls LIMIT 1"
        prepared = await session.create_prepared(simple_query)
        statement = prepared.bind()
        result = await session.execute(statement)
        rows = list(result)
        print(f"✅ Simple query successful! Found {len(rows)} rows")
        
        # Test 2: Create a short URL
        print("\n📝 Test 2: Creating short URL...")
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
        statement.bind(1, 'test456')  # shortcode
        statement.bind(2, url_id)  # id
        statement.bind(3, now)  # created_at
        statement.bind(4, 1)  # created_by_user_id
        statement.bind(5, 'https://example.com/test456')  # original_url
        statement.bind(6, None)  # expiry
        statement.bind(7, 0)  # click_count
        statement.bind(8, now)  # updated_at
        statement.bind(9, False)  # is_private
        statement.bind(10, {'test', 'demo'})  # tags
        
        await session.execute(statement)
        print("✅ Short URL created successfully!")
        
        # Test 3: Retrieve the short URL
        print("\n🔍 Test 3: Retrieving short URL...")
        get_query = """
        SELECT * FROM short_urls
        WHERE namespace_id = ? AND shortcode = ?
        LIMIT 1
        """
        
        get_prepared = await session.create_prepared(get_query)
        get_statement = get_prepared.bind()
        get_statement.bind(0, 1)  # namespace_id
        get_statement.bind(1, 'test456')  # shortcode
        
        result = await session.execute(get_statement)
        rows = list(result)
        
        if rows:
            row = rows[0]
            print(f"✅ Retrieved: {row.shortcode} -> {row.original_url}")
            print(f"   Click count: {row.click_count}")
            print(f"   Tags: {list(row.tags) if row.tags else []}")
        else:
            print("❌ Failed to retrieve short URL")
        
        # Test 4: Delete the short URL
        print("\n🗑️  Test 4: Deleting short URL...")
        delete_query = """
        DELETE FROM short_urls
        WHERE namespace_id = ? AND shortcode = ?
        """
        
        delete_prepared = await session.create_prepared(delete_query)
        delete_statement = delete_prepared.bind()
        delete_statement.bind(0, 1)  # namespace_id
        delete_statement.bind(1, 'test456')  # shortcode
        
        await session.execute(delete_statement)
        print("✅ Short URL deleted!")
        
        # Close connection
        await cluster.close()
        print("\n🎉 All ScyllaDB tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scylla_connection())
