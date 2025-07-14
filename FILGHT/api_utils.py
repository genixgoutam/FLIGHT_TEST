import json
import os
import random

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'file_data.json')

def _load_data():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def fetch_weather():
    data = _load_data()
    return data.get('weather', [])

def fetch_weather_conditions():
    data = _load_data()
    return data.get('weather_conditions', {})

def fetch_fuel_efficiency():
    data = _load_data()
    return data.get('fuel_efficiency', {})

def fetch_safety_factors():
    data = _load_data()
    return data.get('safety_factors', {})

def fetch_operational_constraints():
    data = _load_data()
    return data.get('operational_constraints', {})

def fetch_complexity_metrics():
    data = _load_data()
    return data.get('complexity_metrics', {})

def fetch_optimization_summary():
    data = _load_data()
    return data.get('optimization_summary', {})

def fetch_full_report():
    return _load_data()

def fetch_airspaces(minlon, minlat, maxlon, maxlat):
    data = _load_data()
    airspaces = data.get('airspaces', [])
    if airspaces:
        return random.sample(airspaces, min(3, len(airspaces)))
    return []

def fetch_air_traffic(lamin, lomin, lamax, lomax):
    data = _load_data()
    air_traffic = data.get('air_traffic', [])
    if air_traffic:
        return random.sample(air_traffic, min(5, len(air_traffic)))
    return []

def fetch_all_file_data():
    return _load_data()

# def fetch_flights(dep_iata):
#     url = f"http://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_API_KEY}&dep_iata={dep_iata}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     return None

def fetch_flight_data(air_id):
    data = _load_data()
    flights = data.get('flights', [])
    for flight in flights:
        if flight.get('air_id') == air_id:
            return flight
    return None