"""
Supabase utilities for fetching flight data
"""
import os
import json
from typing import List, Dict, Optional
from supabase import create_client, Client

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed; .env file will not be loaded automatically.")

# Supabase configuration
# You'll need to set these environment variables or add them to settings.py
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

def get_supabase_client() -> Optional[Client]:
    """Get Supabase client instance"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Warning: Supabase credentials not configured")
        return None
    
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None

def fetch_flights_from_supabase(origin_code: str, destination_code: str = None) -> List[Dict]:
    """
    Fetch flight data from Supabase
    
    Args:
        origin_code: Airport code for origin
        destination_code: Optional airport code for destination (for filtering)
    
    Returns:
        List of flight dictionaries
    """
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        # Query flights table - adjust table name and column names as needed
        query = client.table('flights').select('*').eq('origin_code', origin_code)
        
        if destination_code:
            query = query.eq('destination_code', destination_code)
        
        response = query.execute()
        
        if response.data:
            # Convert Supabase response to the expected format
            flights = []
            for flight in response.data:
                flights.append({
                    'flight_number': flight.get('flight_number'),
                    'airline': flight.get('airline'),
                    'departure_time': flight.get('departure_time'),
                    'arrival_time': flight.get('arrival_time'),
                    'status': flight.get('status'),
                    'gate': flight.get('gate'),
                    'terminal': flight.get('terminal'),
                    'aircraft': flight.get('aircraft'),
                    'destination': flight.get('destination_code') or flight.get('destination'),
                })
            return flights
        else:
            print(f"No flights found in Supabase for {origin_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching flights from Supabase: {e}")
        return []

def fetch_air_data_by_id(air_id: int) -> Optional[Dict]:
    """
    Fetch specific air traffic data from Supabase by ID
    
    Args:
        air_id: The ID of the air record to fetch
    
    Returns:
        Dictionary containing the air record data, or None if not found
    """
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return None
    
    try:
        response = client.table('air').select('*').eq('id', air_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"Fetched air record with ID {air_id} from Supabase")
            return response.data[0]
        else:
            print(f"No air record found with ID {air_id}")
            return None
            
    except Exception as e:
        print(f"Error fetching air data by ID {air_id}: {e}")
        return None

def fetch_weather_data_by_id(weather_id: int) -> Optional[Dict]:
    """
    Fetch specific weather data from Supabase by ID
    
    Args:
        weather_id: The ID of the weather record to fetch
    
    Returns:
        Dictionary containing the weather record data, or None if not found
    """
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return None
    
    try:
        response = client.table('weather').select('*').eq('id', weather_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"Fetched weather record with ID {weather_id} from Supabase")
            return response.data[0]
        else:
            print(f"No weather record found with ID {weather_id}")
            return None
            
    except Exception as e:
        print(f"Error fetching weather data by ID {weather_id}: {e}")
        return None

def fetch_fuel_data_by_id(fuel_id: int) -> Optional[Dict]:
    """
    Fetch specific fuel efficiency data from Supabase by ID
    
    Args:
        fuel_id: The ID of the fuel record to fetch
    
    Returns:
        Dictionary containing the fuel record data, or None if not found
    """
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return None
    
    try:
        response = client.table('fuel').select('*').eq('id', fuel_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"Fetched fuel record with ID {fuel_id} from Supabase")
            return response.data[0]
        else:
            print(f"No fuel record found with ID {fuel_id}")
            return None
            
    except Exception as e:
        print(f"Error fetching fuel data by ID {fuel_id}: {e}")
        return None

def fetch_safety_data_by_id(safety_id: int) -> Optional[Dict]:
    """
    Fetch specific safety data from Supabase by ID
    
    Args:
        safety_id: The ID of the safety record to fetch
    
    Returns:
        Dictionary containing the safety record data, or None if not found
    """
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return None
    
    try:
        response = client.table('safety').select('*').eq('id', safety_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"Fetched safety record with ID {safety_id} from Supabase")
            return response.data[0]
        else:
            print(f"No safety record found with ID {safety_id}")
            return None
            
    except Exception as e:
        print(f"Error fetching safety data by ID {safety_id}: {e}")
        return None

def fetch_flight_data_by_id(flight_id: int) -> Optional[Dict]:
    """
    Fetch specific flight data from Supabase by ID
    
    Args:
        flight_id: The ID of the flight record to fetch
    
    Returns:
        Dictionary containing the flight record data, or None if not found
    """
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return None
    
    try:
        response = client.table('flights').select('*').eq('id', flight_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"Fetched flight record with ID {flight_id} from Supabase")
            return response.data[0]
        else:
            print(f"No flight record found with ID {flight_id}")
            return None
            
    except Exception as e:
        print(f"Error fetching flight data by ID {flight_id}: {e}")
        return None

def fetch_weather_data_from_supabase() -> List[Dict]:
    """Fetch weather data from Supabase 'weather' table"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table('weather').select('*').execute()
        if response.data:
            print(f"Fetched {len(response.data)} weather records from Supabase")
            return response.data
        else:
            print("No weather data found in Supabase")
            return []
    except Exception as e:
        print(f"Error fetching weather data from Supabase: {e}")
        return []

def fetch_air_traffic_data_from_supabase() -> List[Dict]:
    """Fetch air traffic data from Supabase 'air' table"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table('air').select('*').execute()
        if response.data:
            print(f"Fetched {len(response.data)} air traffic records from Supabase")
            return response.data
        else:
            print("No air traffic data found in Supabase")
            return []
    except Exception as e:
        print(f"Error fetching air traffic data from Supabase: {e}")
        return []

def fetch_fuel_data_from_supabase() -> List[Dict]:
    """Fetch fuel efficiency data from Supabase 'fuel' table"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table('fuel').select('*').execute()
        if response.data:
            print(f"Fetched {len(response.data)} fuel efficiency records from Supabase")
            return response.data
        else:
            print("No fuel efficiency data found in Supabase")
            return []
    except Exception as e:
        print(f"Error fetching fuel efficiency data from Supabase: {e}")
        return []

def fetch_safety_data_from_supabase() -> List[Dict]:
    """Fetch safety data from Supabase 'safety' table"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table('safety').select('*').execute()
        if response.data:
            print(f"Fetched {len(response.data)} safety records from Supabase")
            return response.data
        else:
            print("No safety data found in Supabase")
            return []
    except Exception as e:
        print(f"Error fetching safety data from Supabase: {e}")
        return []

def fetch_report_data_from_supabase() -> Optional[Dict]:
    """Fetch all report data from Supabase tables"""
    try:
        weather_data = fetch_weather_data_from_supabase()
        air_traffic_data = fetch_air_traffic_data_from_supabase()
        fuel_data = fetch_fuel_data_from_supabase()
        safety_data = fetch_safety_data_from_supabase()
        
        # Combine all data
        report_data = {
            'weather': weather_data,
            'operational_constraints': air_traffic_data,  # Map air table to operational_constraints
            'fuel_efficiency': fuel_data,
            'safety_factors': safety_data,
        }
        
        # Check if we got any data from Supabase
        if any(report_data.values()):
            print("Successfully fetched report data from Supabase tables")
            return report_data
        else:
            print("No data found in Supabase tables")
            return None
            
    except Exception as e:
        print(f"Error fetching report data from Supabase: {e}")
        return None

def insert_sample_data_to_supabase():
    """Insert sample data into Supabase tables"""
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return False
    
    try:
        # Sample weather data
        weather_data = [
            {
                "type": "Clear",
                "severity": "Low",
                "visibility": "10km",
                "wind_speed": "15 km/h",
                "temperature": "22°C",
                "humidity": "65%"
            },
            {
                "type": "Light Rain",
                "severity": "Medium",
                "visibility": "5km",
                "wind_speed": "25 km/h",
                "temperature": "18°C",
                "humidity": "85%"
            }
        ]
        
        # Sample air traffic data
        air_data = [
            {
                "type": "Airspace Restriction",
                "status": "Active",
                "level": "Medium",
                "description": "Military exercise in progress",
                "duration": "2 hours"
            },
            {
                "type": "Runway Maintenance",
                "status": "Scheduled",
                "level": "Low",
                "description": "Minor runway work",
                "duration": "4 hours"
            }
        ]
        
        # Sample fuel efficiency data
        fuel_data = [
            {
                "aircraft_type": "Boeing 737",
                "efficiency": "85%",
                "fuel_consumption": "2.5L/km",
                "emissions": "120g CO2/km",
                "optimization_potential": "15%"
            },
            {
                "aircraft_type": "Airbus A320",
                "efficiency": "88%",
                "fuel_consumption": "2.3L/km",
                "emissions": "110g CO2/km",
                "optimization_potential": "12%"
            }
        ]
        
        # Sample safety data
        safety_data = [
            {
                "factor": "Weather Conditions",
                "value": "Good",
                "score": "85/100",
                "risk_level": "Low",
                "recommendations": "Monitor for changes"
            },
            {
                "factor": "Air Traffic Density",
                "value": "Medium",
                "score": "70/100",
                "risk_level": "Medium",
                "recommendations": "Consider alternative routes"
            }
        ]
        
        # Insert data into tables
        success_count = 0
        
        # Insert weather data
        try:
            response = client.table('weather').insert(weather_data).execute()
            if response.data:
                print(f"Inserted {len(response.data)} weather records")
                success_count += 1
        except Exception as e:
            print(f"Error inserting weather data: {e}")
        
        # Insert air traffic data
        try:
            response = client.table('air').insert(air_data).execute()
            if response.data:
                print(f"Inserted {len(response.data)} air traffic records")
                success_count += 1
        except Exception as e:
            print(f"Error inserting air traffic data: {e}")
        
        # Insert fuel data
        try:
            response = client.table('fuel').insert(fuel_data).execute()
            if response.data:
                print(f"Inserted {len(response.data)} fuel efficiency records")
                success_count += 1
        except Exception as e:
            print(f"Error inserting fuel efficiency data: {e}")
        
        # Insert safety data
        try:
            response = client.table('safety').insert(safety_data).execute()
            if response.data:
                print(f"Inserted {len(response.data)} safety records")
                success_count += 1
        except Exception as e:
            print(f"Error inserting safety data: {e}")
        
        print(f"Successfully inserted data into {success_count}/4 tables")
        return success_count == 4
        
    except Exception as e:
        print(f"Error inserting sample data to Supabase: {e}")
        return False

def save_flights_to_local_file(origin_code: str, flights: List[Dict]) -> bool:
    """
    Save flights data to local JSON file
    
    Args:
        origin_code: Airport code for origin
        flights: List of flight dictionaries
    
    Returns:
        True if successful, False otherwise
    """
    try:
        import os
        from pathlib import Path
        
        # Create static/data directory if it doesn't exist
        data_dir = Path(__file__).parent.parent / 'static' / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to {origin_code}_flights.json
        file_path = data_dir / f"{origin_code}_flights.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(flights, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(flights)} flights to {file_path}")
        return True
        
    except Exception as e:
        print(f"Error saving flights to local file: {e}")
        return False

def fetch_and_save_flights(origin_code: str, destination_code: str = None) -> List[Dict]:
    """
    Fetch flights from Supabase and save to local file
    
    Args:
        origin_code: Airport code for origin
        destination_code: Optional airport code for destination
    
    Returns:
        List of flight dictionaries
    """
    # Fetch from Supabase
    flights = fetch_flights_from_supabase(origin_code, destination_code)
    
    if flights:
        # Save to local file for future use
        save_flights_to_local_file(origin_code, flights)
    
    return flights

def test_supabase_connection():
    """Test Supabase connection by fetching one row from 'flights' table."""
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return False
    try:
        response = client.table('flights').select('*').limit(1).execute()
        if response.data is not None:
            print("Supabase connection successful!")
            return True
        else:
            print("Supabase connection failed: No data returned.")
            return False
    except Exception as e:
        print(f"Supabase connection failed: {e}")
        return False

def download_json_from_supabase_storage(bucket_name: str, file_name: str):
    """
    Download a JSON file from Supabase Storage bucket and return its data.
    Args:
        bucket_name: Name of the Supabase Storage bucket
        file_name: Name of the file to fetch (e.g., 'weather_data.json')
    Returns:
        The parsed JSON data, or None if failed
    """
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return None
    try:
        response = client.storage.from_(bucket_name).download(file_name)
        if hasattr(response, "error") and response.error:
            print(f"Error downloading file: {response.error}")
            return None
        import json
        data = json.loads(response.text())
        print(f"Downloaded {file_name} from bucket {bucket_name}")
        return data
    except Exception as e:
        print(f"Error downloading JSON from Supabase Storage: {e}")
        return None

def upload_report_data_to_supabase_storage(bucket_name: str, data: Dict, file_name: str) -> bool:
    """
    Upload report data to Supabase Storage bucket.
    Args:
        bucket_name: Name of the Supabase Storage bucket
        data: Dictionary data to upload
        file_name: Name of the file to create (e.g., 'weather_data.json')
    Returns:
        True if successful, False otherwise
    """
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return False
    
    try:
        # Convert data to JSON string
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Upload to Supabase Storage
        response = client.storage.from_(bucket_name).upload(
            file_name,
            json_data.encode('utf-8'),
            {"content-type": "application/json"}
        )
        
        if hasattr(response, "error") and response.error:
            print(f"Error uploading file: {response.error}")
            return False
        
        print(f"Successfully uploaded {file_name} to bucket {bucket_name}")
        return True
        
    except Exception as e:
        print(f"Error uploading report data to Supabase Storage: {e}")
        return False

def create_sample_report_data():
    """Create sample report data for testing"""
    weather_data = [
        {
            "type": "Clear",
            "severity": "Low",
            "visibility": "10km",
            "wind_speed": "15 km/h",
            "temperature": "22°C",
            "humidity": "65%"
        },
        {
            "type": "Light Rain",
            "severity": "Medium",
            "visibility": "5km",
            "wind_speed": "25 km/h",
            "temperature": "18°C",
            "humidity": "85%"
        }
    ]
    
    fuel_efficiency_data = [
        {
            "aircraft_type": "Boeing 737",
            "efficiency": "85%",
            "fuel_consumption": "2.5L/km",
            "emissions": "120g CO2/km",
            "optimization_potential": "15%"
        },
        {
            "aircraft_type": "Airbus A320",
            "efficiency": "88%",
            "fuel_consumption": "2.3L/km",
            "emissions": "110g CO2/km",
            "optimization_potential": "12%"
        }
    ]
    
    safety_factors_data = [
        {
            "factor": "Weather Conditions",
            "value": "Good",
            "score": "85/100",
            "risk_level": "Low",
            "recommendations": "Monitor for changes"
        },
        {
            "factor": "Air Traffic Density",
            "value": "Medium",
            "score": "70/100",
            "risk_level": "Medium",
            "recommendations": "Consider alternative routes"
        }
    ]
    
    operational_constraints_data = [
        {
            "type": "Airspace Restriction",
            "status": "Active",
            "level": "Medium",
            "description": "Military exercise in progress",
            "duration": "2 hours"
        },
        {
            "type": "Runway Maintenance",
            "status": "Scheduled",
            "level": "Low",
            "description": "Minor runway work",
            "duration": "4 hours"
        }
    ]
    
    return {
        "weather": weather_data,
        "fuel_efficiency": fuel_efficiency_data,
        "safety_factors": safety_factors_data,
        "operational_constraints": operational_constraints_data
    }

def initialize_supabase_report_data():
    """Initialize Supabase tables with sample report data"""
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return False
    
    try:
        # Insert sample data into tables
        success = insert_sample_data_to_supabase()
        
        if success:
            print("Successfully initialized Supabase tables with sample data")
            return True
        else:
            print("Failed to initialize some Supabase tables")
            return False
        
    except Exception as e:
        print(f"Error initializing Supabase report data: {e}")
        return False

def load_api_flight_data() -> List[Dict]:
    """
    Load flight data from api_flight.json file
    
    Returns:
        List of flight data dictionaries
    """
    try:
        # Path to the api_flight.json file
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data', 'api_flight.json')
        
        if not os.path.exists(json_path):
            print(f"api_flight.json not found at: {json_path}")
            return []
        
        with open(json_path, 'r', encoding='utf-8') as f:
            # Read the file line by line since it contains multiple JSON objects
            data = []
            for line in f:
                line = line.strip()
                if line:
                    try:
                        json_obj = json.loads(line)
                        data.append(json_obj)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON line: {e}")
                        continue
            
            print(f"Loaded {len(data)} flight records from api_flight.json")
            return data
            
    except Exception as e:
        print(f"Error loading api_flight.json: {e}")
        return []

def fetch_flight_data_by_air_id(air_id: str) -> Optional[Dict]:
    """
    Fetch flight data from api_flight.json by air ID
    
    Args:
        air_id: The air ID to search for (e.g., 'BLR', 'OSL', etc.)
    
    Returns:
        Dictionary containing the flight data, or None if not found
    """
    flight_data = load_api_flight_data()
    
    for record in flight_data:
        if record.get('air id') == air_id:
            print(f"Found flight data for air ID: {air_id}")
            return record
    
    print(f"No flight data found for air ID: {air_id}")
    return None

def fetch_all_flight_data() -> List[Dict]:
    """
    Fetch all flight data from api_flight.json
    
    Returns:
        List of all flight data dictionaries
    """
    return load_api_flight_data()

def fetch_flight_data_by_condition(condition: str) -> List[Dict]:
    """
    Fetch flight data from api_flight.json by weather condition
    
    Args:
        condition: Weather condition to filter by (e.g., 'sunny', 'rain', 'cloudy')
    
    Returns:
        List of flight data dictionaries matching the condition
    """
    flight_data = load_api_flight_data()
    
    matching_records = []
    for record in flight_data:
        if record.get('conditions') == condition:
            matching_records.append(record)
    
    print(f"Found {len(matching_records)} records with condition: {condition}")
    return matching_records

def fetch_flight_data_by_alert_status(alert_status: str) -> List[Dict]:
    """
    Fetch flight data from api_flight.json by alert status
    
    Args:
        alert_status: Alert status to filter by (e.g., 'normal', 'warning', 'alert')
    
    Returns:
        List of flight data dictionaries matching the alert status
    """
    flight_data = load_api_flight_data()
    
    matching_records = []
    for record in flight_data:
        if record.get('alert_status') == alert_status:
            matching_records.append(record)
    
    print(f"Found {len(matching_records)} records with alert status: {alert_status}")
    return matching_records

def get_available_air_ids() -> List[str]:
    """
    Get list of all available air IDs from api_flight.json
    
    Returns:
        List of unique air IDs
    """
    flight_data = load_api_flight_data()
    air_ids = list(set(record.get('air id') for record in flight_data if record.get('air id')))
    air_ids.sort()
    return air_ids

def get_available_city() -> list:
    """
    Get list of all available cities from api_flight.json

    Returns:
        List of unique city names
    """
    flight_data = load_api_flight_data()
    cities = list(set(record.get('city') for record in flight_data if record.get('city')))
    cities.sort()
    return cities

def get_available_country() -> list:
    """
    Get list of all available countries from api_flight.json

    Returns:
        List of unique country names
    """
    flight_data = load_api_flight_data()
    countries = list(set(record.get('country') for record in flight_data if record.get('country')))
    countries.sort()
    return countries

def get_available_conditions() -> List[str]:
    """
    Get list of all available weather conditions from api_flight.json
    
    Returns:
        List of unique weather conditions
    """
    flight_data = load_api_flight_data()
    conditions = list(set(record.get('conditions') for record in flight_data if record.get('conditions')))
    conditions.sort()
    return conditions

def get_available_alert_statuses() -> List[str]:
    """
    Get list of all available alert statuses from api_flight.json
    
    Returns:
        List of unique alert statuses
    """
    flight_data = load_api_flight_data()
    alert_statuses = list(set(record.get('alert_status') for record in flight_data if record.get('alert_status')))
    alert_statuses.sort()
    return alert_statuses

def upload_api_flight_data_to_supabase():
    """
    Upload data from api_flight.json to Supabase tables
    This will parse the JSON data and insert it into appropriate tables
    """
    client = get_supabase_client()
    if not client:
        print("Supabase client not initialized.")
        return False
    
    flight_data = load_api_flight_data()
    if not flight_data:
        print("No flight data to upload")
        return False
    
    try:
        # Prepare data for different tables
        weather_records = []
        air_records = []
        fuel_records = []
        safety_records = []
        
        for record in flight_data:
            # Create weather record
            weather_records.append({
                'type': record.get('conditions', 'unknown'),
                'severity': 'Medium',  # Default severity
                'visibility': f"{record.get('distance_km', 0)}km",
                'wind_speed': f"{record.get('wind speed kmh', 0)} km/h",
                'temperature': f"{record.get('temperature', 0)}°C",
                'humidity': f"{record.get('humidity percent', 0)}%"
            })
            
            # Create air record
            air_records.append({
                'type': f"Flight {record.get('air id', 'Unknown')}",
                'status': record.get('alert_status', 'normal'),
                'level': 'Medium' if record.get('alert_status') == 'warning' else 'Low',
                'description': f"Flight monitoring for {record.get('air id', 'Unknown')}",
                'duration': 'Continuous'
            })
            
            # Create fuel record
            fuel_records.append({
                'aircraft_type': 'Commercial Aircraft',
                'efficiency': f"{record.get('fuel_efficiency_kmpl', 0)} km/L",
                'fuel_consumption': f"{record.get('fuel_consumption_lph', 0)} L/h",
                'emissions': f"{record.get('fuel_flow_kgh', 0)} kg/h CO2",
                'optimization_potential': f"{100 - record.get('engine_efficiency_percent', 0)}%"
            })
            
            # Create safety record
            safety_records.append({
                'factor': f"Flight {record.get('air id', 'Unknown')} Safety",
                'value': record.get('alert_status', 'normal'),
                'score': f"{record.get('engine_efficiency_percent', 0)}/100",
                'risk_level': 'Medium' if record.get('alert_status') == 'warning' else 'Low',
                'recommendations': f"Monitor {record.get('air id', 'Unknown')} flight conditions"
            })
        
        # Insert data into tables
        success_count = 0
        
        if weather_records:
            try:
                response = client.table('weather').insert(weather_records).execute()
                if response.data:
                    print(f"Inserted {len(response.data)} weather records")
                    success_count += 1
            except Exception as e:
                print(f"Error inserting weather data: {e}")
        
        if air_records:
            try:
                response = client.table('air').insert(air_records).execute()
                if response.data:
                    print(f"Inserted {len(response.data)} air records")
                    success_count += 1
            except Exception as e:
                print(f"Error inserting air data: {e}")
        
        if fuel_records:
            try:
                response = client.table('fuel').insert(fuel_records).execute()
                if response.data:
                    print(f"Inserted {len(response.data)} fuel records")
                    success_count += 1
            except Exception as e:
                print(f"Error inserting fuel data: {e}")
        
        if safety_records:
            try:
                response = client.table('safety').insert(safety_records).execute()
                if response.data:
                    print(f"Inserted {len(response.data)} safety records")
                    success_count += 1
            except Exception as e:
                print(f"Error inserting safety data: {e}")
        
        print(f"Successfully uploaded data to {success_count}/4 tables")
        return success_count == 4
        
    except Exception as e:
        print(f"Error uploading api_flight data to Supabase: {e}")
        return False