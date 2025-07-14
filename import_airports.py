#!/usr/bin/env python
"""
Import airports from airports_cleaned.json into Django database
"""
import os
import sys
import json
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FILGHT.settings')
django.setup()

from FILGHT.models import Airport

def import_airports_from_json():
    """Import airports from airports_cleaned.json"""
    json_path = os.path.join(os.path.dirname(__file__), 'airports_cleaned.json')
    
    print(f"Loading airports from: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            airports_data = json.load(f)
        
        print(f"Found {len(airports_data)} airports in JSON file")
        
        airports_created = 0
        airports_skipped = 0
        
        for airport_data in airports_data:
            try:
                # Defensive: skip if required fields are missing
                if not airport_data.get('code') or not airport_data.get('name'):
                    airports_skipped += 1
                    continue
                
                location = airport_data.get('location', {})
                
                # Check if airport already exists
                existing_airport = Airport.objects.filter(code=airport_data['code']).first()
                
                if existing_airport:
                    airports_skipped += 1
                    continue
                
                # Map 'country' to 'place' and 'city' to 'city' for template compatibility
                airport = Airport.objects.create(
                    code=airport_data['code'],
                    name=airport_data['name'],
                    latitude=Decimal(str(airport_data.get('latitude', 0))),
                    longitude=Decimal(str(airport_data.get('longitude', 0))),
                    timezone=airport_data.get('timezone', 'UTC'),
                    country=location.get('country', ''),  # 'place' is used as country
                    city=location.get('city', ''),      # 'city' is used as city
                    type=airport_data.get('type', ''),
                    # elevation = airport_data.get('elevation'),
                )
                
                airports_created += 1
                
                if airports_created % 100 == 0:
                    print(f"Created {airports_created} airports...")
                    
            except Exception as e:
                print(f"Error creating airport {airport_data.get('code', 'Unknown')}: {e}")
                continue
        
        print(f"\nImport completed!")
        print(f"Airports created: {airports_created}")
        print(f"Airports skipped (already exist): {airports_skipped}")
        print(f"Total airports in database: {Airport.objects.count()}")
        
    except FileNotFoundError:
        print(f"Error: File not found at {json_path}")
    except Exception as e:
        print(f"Error loading JSON file: {e}")

def main():
    """Main function"""
    print("Importing airports from airports_cleaned.json...")
    print("=" * 50)
    
    import_airports_from_json()
    
    print("\n" + "=" * 50)
    print("Airport import completed!")
    print("You can now use these airports in your flight search!")

if __name__ == "__main__":
    main()