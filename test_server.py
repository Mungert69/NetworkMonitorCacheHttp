#!/usr/bin/env python3
"""
Test script for the Flask Cache Server.

This script tests all the main endpoints of the cache server to ensure they work correctly.
"""

import requests
import hashlib

# Configuration
BASE_URL = "http://localhost:5000"
API_KEY = "test-api-key"
TEST_CONTENT = b"This is a test LLM context file content for testing the cache server functionality."

def get_test_hash(content):
    """Generate SHA256 hash of content."""
    return hashlib.sha256(content).hexdigest()

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_file_check():
    """Test checking if a file exists."""
    print("Testing file existence check...")
    test_hash = get_test_hash(TEST_CONTENT)
    
    try:
        response = requests.head(
            f"{BASE_URL}/cache/{test_hash}",
            headers={"X-API-Key": API_KEY}
        )
        if response.status_code in (200, 404):
            print(f"✅ File check passed: status = {response.status_code}")
            return True
        else:
            print(f"❌ File check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File check error: {e}")
        return False

def test_file_upload():
    """Test uploading a file."""
    print("Testing file upload...")
    test_hash = get_test_hash(TEST_CONTENT)
    
    try:
        response = requests.put(
            f"{BASE_URL}/cache/{test_hash}",
            headers={"X-API-Key": API_KEY},
            data=TEST_CONTENT
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ File upload passed: {result}")
            return True
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return False

def test_file_download():
    """Test downloading a file."""
    print("Testing file download...")
    test_hash = get_test_hash(TEST_CONTENT)
    
    try:
        response = requests.get(
            f"{BASE_URL}/cache/{test_hash}",
            headers={"X-API-Key": API_KEY}
        )
        if response.status_code == 200:
            downloaded_content = response.content
            if downloaded_content == TEST_CONTENT:
                print("✅ File download passed: content matches")
                return True
            else:
                print("❌ File download failed: content mismatch")
                return False
        else:
            print(f"❌ File download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File download error: {e}")
        return False

def test_list_files():
    """Test listing cached files."""
    print("Testing file listing...")
    try:
        response = requests.get(
            f"{BASE_URL}/cache/files",
            headers={"X-API-Key": API_KEY}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File listing passed: {result.get('count')} files")
            return True
        else:
            print(f"❌ File listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File listing error: {e}")
        return False

def test_file_delete():
    """Test deleting a file."""
    print("Testing file deletion...")
    test_hash = get_test_hash(TEST_CONTENT)

    try:
        response = requests.delete(
            f"{BASE_URL}/cache/{test_hash}",
            headers={"X-API-Key": API_KEY}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File deletion passed: {result}")
            return True
        else:
            print(f"❌ File deletion failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File deletion error: {e}")
        return False

def test_unauthorized_access():
    """Test unauthorized access."""
    print("Testing unauthorized access...")
    try:
        response = requests.get(f"{BASE_URL}/cache/test")
        if response.status_code == 401:
            print("✅ Unauthorized access correctly blocked")
            return True
        else:
            print(f"❌ Unauthorized access not blocked: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Unauthorized access test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Starting Flask Cache Server Tests")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_unauthorized_access,  # Test this first
        test_file_check,
        test_file_upload,
        test_file_download,
        test_list_files,
        test_file_delete,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Flask Cache Server is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server configuration.")
    
    return passed == total

if __name__ == "__main__":
    main()
