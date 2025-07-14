#!/usr/bin/env python3
"""
Example: How to fetch air traffic data from Supabase using air ID
This script demonstrates different ways to get air data by ID
"""

import os
import sys
import django
import requests

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FILGHT.settings')
django.setup()

from FILGHT.supabase_utils import fetch_air_data_by_id

def example_direct_supabase():
    """Example: Fetch air data directly from Supabase using ID"""
    print("🔍 Example 1: Direct Supabase Function")
    print("=" * 50)
    
    # Fetch air data with ID 1
    air_id = 1
    air_data = fetch_air_data_by_id(air_id)
    
    if air_data:
        print(f"✅ Successfully fetched air data for ID {air_id}:")
        print(f"   Type: {air_data.get('type')}")
        print(f"   Status: {air_data.get('status')}")
        print(f"   Level: {air_data.get('level')}")
        print(f"   Description: {air_data.get('description')}")
        print(f"   Duration: {air_data.get('duration')}")
        print(f"   Created: {air_data.get('created_at')}")
    else:
        print(f"❌ No air data found for ID {air_id}")
    
    return air_data

def example_api_endpoint():
    """Example: Fetch air data using API endpoint"""
    print("\n🌐 Example 2: API Endpoint")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    air_id = 1
    
    try:
        response = requests.get(f"{base_url}/api/air/{air_id}/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                air_data = data.get('data')
                print(f"✅ Successfully fetched air data for ID {air_id} via API:")
                print(f"   Type: {air_data.get('type')}")
                print(f"   Status: {air_data.get('status')}")
                print(f"   Level: {air_data.get('level')}")
                print(f"   Description: {air_data.get('description')}")
                print(f"   Duration: {air_data.get('duration')}")
                print(f"   Source: {data.get('source')}")
            else:
                print(f"❌ API returned error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        print("   Make sure Django server is running: python manage.py runserver")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    return None

def example_multiple_ids():
    """Example: Fetch multiple air records by different IDs"""
    print("\n📋 Example 3: Multiple IDs")
    print("=" * 50)
    
    air_ids = [1, 2, 3]  # Try different IDs
    
    for air_id in air_ids:
        print(f"\nFetching air data for ID {air_id}:")
        air_data = fetch_air_data_by_id(air_id)
        
        if air_data:
            print(f"✅ Found: {air_data.get('type')} - {air_data.get('status')}")
        else:
            print(f"❌ Not found")

def example_error_handling():
    """Example: Proper error handling when fetching by ID"""
    print("\n🛡️ Example 4: Error Handling")
    print("=" * 50)
    
    # Test with invalid ID
    invalid_id = 999
    print(f"Testing with invalid ID: {invalid_id}")
    
    try:
        air_data = fetch_air_data_by_id(invalid_id)
        if air_data:
            print(f"✅ Found data: {air_data}")
        else:
            print(f"✅ Correctly returned None for invalid ID")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
    
    # Test with string ID (should handle gracefully)
    string_id = "abc"
    print(f"\nTesting with string ID: {string_id}")
    
    try:
        air_data = fetch_air_data_by_id(string_id)
        if air_data:
            print(f"✅ Found data: {air_data}")
        else:
            print(f"✅ Correctly returned None for string ID")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def main():
    """Run all examples"""
    print("🚁 Air ID Fetching Examples")
    print("=" * 60)
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Environment variables not set!")
        print("   Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return
    
    print(f"✅ Environment variables found")
    
    # Run examples
    example_direct_supabase()
    example_api_endpoint()
    example_multiple_ids()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("📚 Usage Summary:")
    print("=" * 60)
    print("1. Direct function call:")
    print("   air_data = fetch_air_data_by_id(1)")
    print()
    print("2. API endpoint call:")
    print("   GET /api/air/1/")
    print()
    print("3. In your Django views:")
    print("   from .supabase_utils import fetch_air_data_by_id")
    print("   air_record = fetch_air_data_by_id(air_id)")
    print("   if air_record:")
    print("       # Process the data")
    print("       type = air_record.get('type')")
    print("       status = air_record.get('status')")
    print()
    print("4. In your templates:")
    print("   <script>")
    print("   fetch('/api/air/1/')")
    print("       .then(response => response.json())")
    print("       .then(data => {")
    print("           if (data.success) {")
    print("               console.log(data.data);")
    print("           }")
    print("       });")
    print("   </script>")

if __name__ == "__main__":
    main() 