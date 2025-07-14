from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Airport, Flight, WeatherCondition, FuelEfficiency, SafetyFactor, OperationalConstraint
from .api_utils import fetch_all_file_data, fetch_full_report, fetch_flight_data
from rest_framework import generics, views, status
from rest_framework.response import Response
from .serializers import (
    AirportSerializer, FlightSerializer, WeatherConditionSerializer,
    FuelEfficiencySerializer, SafetyFactorSerializer, OperationalConstraintSerializer
)
from .supabase_utils import (
    fetch_and_save_flights, 
    fetch_report_data_from_supabase, 
    get_supabase_client, 
    initialize_supabase_report_data,
    fetch_air_data_by_id,
    fetch_weather_data_by_id,
    fetch_fuel_data_by_id,
    fetch_safety_data_by_id,
    fetch_flight_data_by_id,
    load_api_flight_data,
    fetch_flight_data_by_air_id,
    fetch_all_flight_data,
    fetch_flight_data_by_condition,
    fetch_flight_data_by_alert_status,
    get_available_air_ids,
    get_available_conditions,
    get_available_alert_statuses,
    upload_api_flight_data_to_supabase
)
import json
import os
from datetime import timedelta
import requests
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import math
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
import numpy as np
import tensorflow as tf

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def calculate_route_distance(route_coordinates):
    """Calculate total distance for a route"""
    total_distance = 0
    for i in range(len(route_coordinates) - 1):
        lat1, lon1 = route_coordinates[i]
        lat2, lon2 = route_coordinates[i + 1]
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        total_distance += distance
    return total_distance

def estimate_flight_time(distance_km, avg_speed_kmh=800):
    """Estimate flight time based on distance and average speed"""
    # Add 30 minutes for takeoff and landing
    time_hours = (distance_km / avg_speed_kmh) + 0.5
    hours = int(time_hours)
    minutes = int((time_hours - hours) * 60)
    return hours, minutes

def calculate_fuel_cost(distance_km, fuel_price_per_liter=0.8, fuel_consumption_lph=2500):
    """Calculate fuel cost based on distance and fuel consumption"""
    # Average fuel consumption: 2500 liters per hour for commercial aircraft
    # Average speed: 800 km/h
    flight_hours = distance_km / 800
    fuel_consumed = flight_hours * fuel_consumption_lph
    fuel_cost = fuel_consumed * fuel_price_per_liter
    return fuel_cost

def calculate_total_cost(distance_km, base_cost_per_km=1.2):
    """Calculate total operational cost including fuel, maintenance, crew, etc."""
    fuel_cost = calculate_fuel_cost(distance_km)
    # Operational costs include: maintenance, crew, landing fees, insurance, etc.
    operational_cost = distance_km * base_cost_per_km
    total_cost = fuel_cost + operational_cost
    return total_cost, fuel_cost

load_dotenv()

# Load airports from airports_cleaned.json
AIRPORTS_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'airports_cleaned.json')
with open(AIRPORTS_JSON_PATH, 'r', encoding='utf-8') as f:
    AIRPORTS = json.load(f)

AIRPORT_CODES = [a['code'] for a in AIRPORTS]

# Compute DIST_MATRIX using Euclidean distance between airport coordinates
DIST_MATRIX = {}
for a in AIRPORTS:
    for b in AIRPORTS:
        if a['code'] != b['code']:
            dist = math.sqrt((a['latitude'] - b['latitude']) ** 2 + (a['longitude'] - b['longitude']) ** 2)
            DIST_MATRIX[(a['code'], b['code'])] = dist

def home(request):
    """Render the homepage"""
    return render(request, 'home.html')

def dijkstra(start, end, codes, dist_matrix):
    import heapq
    graph = {code: [] for code in codes}
    for (a, b), d in dist_matrix.items():
        graph[a].append((b, d))
    queue = [(0, start, [start])]
    visited = set()
    while queue:
        cost, node, path = heapq.heappop(queue)
        if node == end:
            return path
        if node in visited:
            continue
        visited.add(node)
        for neighbor, weight in graph[node]:
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path + [neighbor]))
    return [start, end]  # fallback


def find_alternatives(main_path, codes):
    # For demo: swap one intermediate stop to create alternatives
    alternatives = []
    # Use all available airport codes except the origin and destination
    for alt in codes:
        if alt not in main_path:
            alt_path = [main_path[0], alt, main_path[-1]]
            alternatives.append(alt_path)
        if len(alternatives) == 2:
            break
    return alternatives

from django.views import View

class OptimizeView(View):
    def get(self, request):
        airports = Airport.objects.all()
        return render(request, 'optimize.html', {'airports': airports})

    def post(self, request):
        import json
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            origin_id = data.get('origin')
            destination_id = data.get('destination')
        else:
            origin_id = request.POST.get('origin')
            destination_id = request.POST.get('destination')

        airports = Airport.objects.all()
        airport_id_map = {str(a.id): a.code for a in airports}
        origin = airport_id_map.get(origin_id)
        destination = airport_id_map.get(destination_id)
        
        if not origin or not destination or origin == destination:
            response = {
                'error': 'Invalid origin or destination',
                'all_routes': [],
            }
            return JsonResponse(response)

        # Dummy QUBO matrix (replace with real logic)
        qubo_matrix = [[0]*8 for _ in range(8)]
        # Call QAOA API (dummy call, replace with real logic)
        import requests
        api_url = 'http://127.0.0.1:8000/api/qaoa-predict/'
        try:
            qaoa_response = requests.post(api_url, json={'qubo_matrix': qubo_matrix})
            qaoa_result = qaoa_response.json()
        except Exception as e:
            qaoa_result = {'error': str(e)}
        # Find shortest path and alternatives
        main_path = dijkstra(origin, destination, AIRPORT_CODES, DIST_MATRIX)
        alt_paths = find_alternatives(main_path, AIRPORT_CODES)
        airport_dict = {a['code']: a for a in AIRPORTS}
        def build_route_obj(codes):
            coords = [[airport_dict[code]['latitude'], airport_dict[code]['longitude']] for code in codes if code in airport_dict]
            path = ' → '.join(codes)
            return {'coordinates': coords, 'path': path}
        all_routes = [build_route_obj(main_path)] + [build_route_obj(alt) for alt in alt_paths]

        # Calculate real timing, cost, and optimization data for the main route
        main_route = all_routes[0] if all_routes else None
        if main_route and main_route['coordinates']:
            # Calculate real distance
            total_distance_km = calculate_route_distance(main_route['coordinates'])
            total_distance_miles = total_distance_km * 0.621371  # Convert km to miles
            
            # Calculate real flight time
            hours, minutes = estimate_flight_time(total_distance_km)
            
            # Calculate real costs
            total_cost, fuel_cost = calculate_total_cost(total_distance_km)
            
            timing_data = {
                'estimated_duration_hours': hours,
                'estimated_duration_minutes': minutes,
                'total_distance_miles': round(total_distance_miles, 2),
                'total_distance_km': round(total_distance_km, 2),
            }
            
            cost_data = {
                'total_cost': round(total_cost, 2),
                'total_fuel_cost': round(fuel_cost, 2),
            }
            
            optimization_data = {
                'method': 'QAOA',
                'total_distance': round(total_distance_miles, 2),
                'total_cost': round(total_cost, 2),
                'path': main_route['path'],
            }
        else:
            # Fallback to dummy data if no route
            timing_data = {
                'estimated_duration_hours': 0,
                'estimated_duration_minutes': 0,
                'total_distance_miles': 0,
                'total_distance_km': 0,
            }
            cost_data = {
                'total_cost': 0,
                'total_fuel_cost': 0,
            }
            optimization_data = {
                'method': 'QAOA',
                'total_distance': 0,
                'total_cost': 0,
                'path': '',
            }

        # Calculate data for all routes (main + alternatives)
        all_routes_data = []
        for route in all_routes:
            if route and route['coordinates']:
                distance_km = calculate_route_distance(route['coordinates'])
                distance_miles = distance_km * 0.621371
                hours, minutes = estimate_flight_time(distance_km)
                total_cost, fuel_cost = calculate_total_cost(distance_km)
                
                route_data = {
                    **route,
                    'distance_km': round(distance_km, 2),
                    'distance_miles': round(distance_miles, 2),
                    'duration_hours': hours,
                    'duration_minutes': minutes,
                    'total_cost': round(total_cost, 2),
                    'fuel_cost': round(fuel_cost, 2),
                }
                all_routes_data.append(route_data)
            else:
                all_routes_data.append(route)

        response = {
            'all_routes': all_routes_data,
            'route': {
                'path': main_route['path'] if main_route else '',
                'timing': timing_data,
                'total_cost': cost_data['total_cost'],
                'total_fuel_cost': cost_data['total_fuel_cost'],
            },
            'optimization_results': optimization_data,
            'qaoa_result': qaoa_result,
        }
        return JsonResponse(response)

def choices_view(request):
    """View to get choices for origin, destination, and airline"""
    airports = Airport.objects.all()
    airlines = Flight.objects.values_list('airline', flat=True).distinct().order_by('airline')
    
    return render(request, 'choices.html', {
        'airports': airports,
        'airlines': airlines
    })

def flight_info(request):
    """View to see all flight information"""
    airports = list(Airport.objects.values('id', 'code', 'name', 'latitude', 'longitude'))
    flight_data = None
    
    if request.method == 'POST':
        origin_code = request.POST.get('origin_code')
        destination_code = request.POST.get('destination_code')
        
        # Load data from DEL_to_BOM_flights.json
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'DEL_to_BOM_flights.json')
        print(f"JSON path: {json_path}")
        print(f"Loading JSON from: {json_path}")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            print(f"Loaded {len(json_data.get('schedules', []))} schedules and {len(json_data.get('prices', []))} prices")
            
            flight_data = {
                'origin': origin_code,
                'destination': destination_code,
                'schedules': json_data.get('schedules', []),
                'prices': json_data.get('prices', [])
            }
        except FileNotFoundError:
            print(f"File not found: {json_path}")
            flight_data = {
                'origin': origin_code,
                'destination': destination_code,
                'schedules': [],
                'prices': []
            }
        except Exception as e:
            print(f"Error loading JSON: {e}")
            flight_data = {
                'origin': origin_code,
                'destination': destination_code,
                'schedules': [],
                'prices': []
            }
    
    print(f"Passing {len(airports)} airports to template")
    return render(request, 'flight_info.html', {
        'airports': airports,
        'flight_data': flight_data
    })

def map_view(request):
    """View for displaying route maps"""
    return render(request, 'map.html')

def show_file_data(request):
    file_data = fetch_all_file_data()
    return render(request, 'optimize.html', {'file_data': file_data})

def api_airports(request):
    airports = list(Airport.objects.all().values('code', 'name', 'latitude', 'longitude'))
    return JsonResponse({"airports": airports})

def api_air_traffic(request):
    # Load air_traffic from file_data.json
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'file_data.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        file_data = json.load(f)
    air_traffic = file_data.get('air_traffic', [])
    # For demo, add random positions near Goa (if not present)
    for plane in air_traffic:
        if 'latitude' not in plane or 'longitude' not in plane:
            # Randomize near Goa
            import random
            plane['latitude'] = 15.3 + random.uniform(-0.3, 0.3)
            plane['longitude'] = 73.8 + random.uniform(-0.3, 0.3)
    return JsonResponse({'air_traffic': air_traffic})

def api_stops(request):
    stops = list(Airport.objects.all().values('code', 'name', 'latitude', 'longitude', 'country'))
    return JsonResponse({'stops': stops})

def api_all_airports(request):
    """
    API endpoint to fetch airports from airports.json with optional filtering.
    Query params:
      - country: filter by country (case-insensitive, partial match)
      - city: filter by city (case-insensitive, partial match)
      - code: filter by airport code (case-insensitive, exact match)
    """
    import os, json
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'airports_cleaned.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        airports = json.load(f)

    country = request.GET.get('country', '').strip().lower()
    city = request.GET.get('city', '').strip().lower()
    code = request.GET.get('code', '').strip().upper()

    def match(airport):
        loc = airport.get('location', {})
        matches = True
        if country:
            matches = matches and country in loc.get('country', '').lower()
        if city:
            matches = matches and city in loc.get('city', '').lower()
        if code:
            matches = matches and code == airport.get('code', '').upper()
        return matches

    if country or city or code:
        airports = [a for a in airports if match(a)]

    return JsonResponse({'airports': airports})

def report_view(request):
    """Report view that fetches data from api_flight.json"""
    from .supabase_utils import (
        load_api_flight_data,
        fetch_flight_data_by_air_id,
        get_available_air_ids,
        get_available_city,
        get_available_country,
        get_available_conditions,
        get_available_alert_statuses
    )
    
    # Load data from api_flight.json
    print("Loading api_flight.json data...")
    api_flight_data = load_api_flight_data()
    print(f"Loaded {len(api_flight_data) if api_flight_data else 0} records from api_flight.json")
    
    if api_flight_data:
        print("Sample record:", api_flight_data[0] if api_flight_data else "No data")
        # Transform api_flight.json data into the expected report format
        weather_data = []
        air_traffic_data = []
        fuel_efficiency_data = []
        safety_factors_data = []
        
        for record in api_flight_data:
            # Weather data
            weather_data.append({
                'type': record.get('conditions', 'unknown'),
                'severity': 'Medium',  # Default severity
                'visibility': f"{record.get('distance_km', 0)}km",
                'wind_speed': f"{record.get('wind speed kmh', 0)} km/h",
                'temperature': f"{record.get('temperature', 0)}°C",
                'humidity': f"{record.get('humidity percent', 0)}%",
                'pressure': f"{record.get('pressure hpa', 0)} hPa",
                'precipitation': f"{record.get('precipitation mm', 0)} mm"
            })
            
            # Air traffic data
            air_traffic_data.append({
                'type': f"Flight {record.get('air id', 'Unknown')}",
                'status': record.get('alert_status', 'normal'),
                'level': 'Medium' if record.get('alert_status') == 'warning' else 'Low',
                'description': f"Flight monitoring for {record.get('air id', 'Unknown')}",
                'duration': 'Continuous',
                'altitude': f"{record.get('altitude_ft', 0)} ft",
                'speed': f"{record.get('speed_knots', 0)} knots",
                'heading': f"{record.get('heading_deg', 0)}°"
            })
            
            # Fuel efficiency data
            fuel_efficiency_data.append({
                'aircraft_type': 'Commercial Aircraft',
                'efficiency': f"{record.get('fuel_efficiency_kmpl', 0)} km/L",
                'fuel_consumption': f"{record.get('fuel_consumption_lph', 0)} L/h",
                'emissions': f"{record.get('fuel_flow_kgh', 0)} kg/h CO2",
                'optimization_potential': f"{100 - record.get('engine_efficiency_percent', 0)}%",
                'engine_rpm': record.get('engine_rpm', 0),
                'fuel_remaining': f"{record.get('fuel_remaining_kg', 0)} kg"
            })
            
            # Safety factors data
            safety_factors_data.append({
                'factor': f"Flight {record.get('air id', 'Unknown')} Safety",
                'value': record.get('alert_status', 'normal'),
                'score': f"{record.get('engine_efficiency_percent', 0)}/100",
                'risk_level': 'Medium' if record.get('alert_status') == 'warning' else 'Low',
                'recommendations': f"Monitor {record.get('air id', 'Unknown')} flight conditions",
                'vibration_level': record.get('vibration_level', 0),
                'tilt_angle': f"{record.get('tilt_angle_deg', 0)}°"
            })
        
        report_data = {
            'weather': weather_data,
            'operational_constraints': air_traffic_data,
            'fuel_efficiency': fuel_efficiency_data,
            'safety_factors': safety_factors_data
        }
        
        data_source = "api_flight"
        print(f"Created report data with {len(weather_data)} weather records, {len(air_traffic_data)} air traffic records")
    else:
        # Fallback to empty data if api_flight.json is not available
        report_data = {
            'weather': [],
            'operational_constraints': [],
            'fuel_efficiency': [],
            'safety_factors': []
        }
        data_source = "none"
        print("No api_flight.json data available, using empty report data")
    
    # Build unique airport list for dropdowns
    airports = [
        {
            "airid": record.get("air id"),
            "city": record.get("city"),
            "country": record.get("country")
        }
        for record in api_flight_data
        if record.get("air id") and record.get("city") and record.get("country")
    ]
    seen = set()
    unique_airports = []
    for airport in airports:
        key = (airport["airid"], airport["city"], airport["country"])
        if key not in seen:
            seen.add(key)
            unique_airports.append(airport)

    context = {
        'report': report_data,
        'data_source': data_source,
        'api_flight_data': api_flight_data,
        'airports': unique_airports
    }
    
    print(f"Rendering report template with {len(api_flight_data) if api_flight_data else 0} flight records")
    return render(request, 'report.html', context)

def fetch_report_data_from_supabase():
    """Fetch report data from Supabase tables"""
    from .supabase_utils import fetch_report_data_from_supabase as fetch_supabase_data
    return fetch_supabase_data()

def api_flights_json(request):
    """API endpoint to serve DEL-BOM flight data from DEL_to_BOM_flights.json"""
    print("API flights endpoint called")
    origin_id = request.GET.get('origin')
    destination_id = request.GET.get('destination')
    print(f"Origin ID: {origin_id}, Destination ID: {destination_id}")
    
    # Get airport codes for the given IDs
    try:
        origin_code = Airport.objects.get(id=origin_id).code if origin_id else None
        destination_code = Airport.objects.get(id=destination_id).code if destination_id else None
        print(f"Origin code: {origin_code}, Destination code: {destination_code}")
    except Airport.DoesNotExist:
        print("Airport not found")
        return JsonResponse({'error': 'Invalid airport IDs'}, status=400)

    # Only serve data for DEL <-> BOM
    valid_pairs = [
        ('DEL', 'BOM'),
        ('BOM', 'DEL'),
    ]
    print(f"Checking if ({origin_code}, {destination_code}) is in valid pairs")
    if (origin_code, destination_code) in valid_pairs:
        print("Valid pair found, fetching flight data")
        try:
            data = fetch_flight_data()
            print(f"Fetched data: {len(data.get('schedules', []))} schedules, {len(data.get('prices', []))} prices")
            # Format for frontend JS
            flights = []
            for s, p in zip(data.get('schedules', []), data.get('prices', [])):
                flights.append({
                    'flight_number': s.get('flight_number'),
                    'airline_name': s.get('airline'),
                    'departure_time': s.get('departure_time'),
                    'arrival_time': s.get('arrival_time'),
                    'duration': p.get('duration'),
                    'price': f"{p.get('price')} {p.get('currency')}"
                })
            print(f"Returning {len(flights)} flights")
            return JsonResponse({'flights': flights})
        except Exception as e:
            print(f"Error fetching flight data: {e}")
            return JsonResponse({'error': f'Error loading flight data: {str(e)}'}, status=500)
    else:
        print("Invalid pair, returning empty flights")
        return JsonResponse({'flights': []})

def api_flights_dynamic(request):
    """Dynamic API endpoint to serve flight data from multiple JSON files and database"""
    
    if request.method == 'POST':
        # Handle POST request to save flight data
        try:
            data = json.loads(request.body)
            origin_code = data.get('origin_code')
            destination_code = data.get('destination_code')
            flight_data = data.get('flight_data', [])
            
            # Get airport objects
            origin = Airport.objects.get(code=origin_code)
            destination = Airport.objects.get(code=destination_code)
            
            saved_count = 0
            for flight_info in flight_data:
                # Handle both old and new format
                airline = flight_info.get('airline_name') or flight_info.get('airline', 'Unknown')
                aircraft = flight_info.get('aircraft', 'Unknown')
                departure_time = flight_info.get('departure_time', '00:00:00')
                arrival_time = flight_info.get('arrival_time', '00:00:00')
                
                # Create or update flight
                flight, created = Flight.objects.get_or_create(
                    flight_number=flight_info.get('flight_number'),
                    origin=origin,
                    destination=destination,
                    defaults={
                        'airline': airline,
                        'price': flight_info.get('price', 0),
                        'currency': 'USD',
                        'departure_time': departure_time,
                        'arrival_time': arrival_time,
                        'duration': timedelta(hours=3),  # Default duration
                        'aircraft_type': aircraft,
                    }
                )
                if created:
                    saved_count += 1
            
            return JsonResponse({
                'message': f'Successfully saved {saved_count} flights to database',
                'saved_count': saved_count
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error saving flight data: {str(e)}'}, status=400)
    
    # Handle GET request (existing code)
    origin_id = request.GET.get('origin')
    destination_id = request.GET.get('destination')
    
    print(f"Dynamic API called - Origin ID: {origin_id}, Destination ID: {destination_id}")
    
    # Get airport codes for the given IDs
    try:
        origin_code = Airport.objects.get(id=origin_id).code if origin_id else None
        destination_code = Airport.objects.get(id=destination_id).code if destination_id else None
        print(f"Airport codes - Origin: {origin_code}, Destination: {destination_code}")
    except Airport.DoesNotExist:
        return JsonResponse({'error': 'Invalid airport IDs'}, status=400)

    # Try to get data from database first
    db_flights = Flight.objects.filter(
        origin__code=origin_code, 
        destination__code=destination_code
    )
    
    flights = []
    
    # Add database flights
    for flight in db_flights:
        flights.append({
            'flight_number': flight.flight_number,
            'airline_name': flight.airline,
            'departure_time': str(flight.departure_time),
            'arrival_time': str(flight.arrival_time),
            'duration': str(flight.duration),
            'price': f"{flight.price} {flight.currency}",
            'source': 'database'
        })
    
    # Try to get data from JSON files
    # First try the old format: {origin}_to_{destination}_flights.json
    json_filename = f"{origin_code}_to_{destination_code}_flights.json"
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data', json_filename)
    
    print(f"Looking for JSON file: {json_path}")
    
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Check if the JSON data is a list (new format) or has schedules/prices (old format)
            if isinstance(json_data, list):
                print(f"Found JSON data: {len(json_data)} flights (new format)")
                
                # New format: each object is a flight with destination field
                for flight_obj in json_data:
                    # Check if this flight matches the requested destination
                    flight_destination = flight_obj.get('destination')
                    if flight_destination == destination_code:
                        flights.append({
                            'flight_number': flight_obj.get('flight_number'),
                            'airline_name': flight_obj.get('airline'),
                            'departure_time': flight_obj.get('departure_time'),
                            'arrival_time': flight_obj.get('arrival_time'),
                            'duration': '3h',  # Default duration
                            'price': 'N/A USD',  # Default price
                            'status': flight_obj.get('status'),
                            'gate': flight_obj.get('gate'),
                            'terminal': flight_obj.get('terminal'),
                            'aircraft': flight_obj.get('aircraft'),
                            'destination': flight_obj.get('destination'),
                            'source': 'json_file_new_format'
                        })
            else:
                # Old format: schedules and prices arrays
                print(f"Found JSON data: {len(json_data.get('schedules', []))} schedules (old format)")
                
                schedules = json_data.get('schedules', [])
                prices = json_data.get('prices', [])
                
                for i, schedule in enumerate(schedules):
                    price_data = prices[i] if i < len(prices) else {}
                    flights.append({
                        'flight_number': schedule.get('flight_number'),
                        'airline_name': schedule.get('airline'),
                        'departure_time': schedule.get('departure_time'),
                        'arrival_time': schedule.get('arrival_time'),
                        'duration': price_data.get('duration', '3h'),
                        'price': f"{price_data.get('price', 'N/A')} {price_data.get('currency', 'USD')}",
                        'status': schedule.get('status'),
                        'gate': schedule.get('gate'),
                        'terminal': schedule.get('terminal'),
                        'aircraft': schedule.get('aircraft'),
                        'source': 'json_file_old_format'
                    })
        else:
            print(f"JSON file not found: {json_path}")
            
    except Exception as e:
        print(f"Error reading JSON file: {e}")
    
    # If no data found, try the new format: {origin}_flights.json
    if not flights:
        new_format_filename = f"{origin_code}_flights.json"
        new_format_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data', new_format_filename)
        
        print(f"Looking for new format JSON file: {new_format_path}")
        
        try:
            if os.path.exists(new_format_path):
                with open(new_format_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                if isinstance(json_data, list):
                    print(f"Found new format JSON data: {len(json_data)} flights")
                    
                    # Filter flights by destination
                    for flight_obj in json_data:
                        flight_destination = flight_obj.get('destination')
                        if flight_destination == destination_code:
                            flights.append({
                                'flight_number': flight_obj.get('flight_number'),
                                'airline_name': flight_obj.get('airline'),
                                'departure_time': flight_obj.get('departure_time'),
                                'arrival_time': flight_obj.get('arrival_time'),
                                'duration': '3h',  # Default duration
                                'price': 'N/A USD',  # Default price
                                'status': flight_obj.get('status'),
                                'gate': flight_obj.get('gate'),
                                'terminal': flight_obj.get('terminal'),
                                'aircraft': flight_obj.get('aircraft'),
                                'destination': flight_obj.get('destination'),
                                'source': 'json_file_new_format'
                            })
                else:
                    print(f"New format file exists but is not a list: {new_format_path}")
            else:
                print(f"New format JSON file not found: {new_format_path}")
                
                # Try to fetch from Supabase
                print(f"Attempting to fetch flights from Supabase for {origin_code}")
                try:
                    supabase_flights = fetch_and_save_flights(origin_code, destination_code)
                    if supabase_flights:
                        print(f"Successfully fetched {len(supabase_flights)} flights from Supabase")
                        
                        # Filter flights by destination if specified
                        for flight_obj in supabase_flights:
                            if not destination_code or flight_obj.get('destination') == destination_code:
                                flights.append({
                                    'flight_number': flight_obj.get('flight_number'),
                                    'airline_name': flight_obj.get('airline'),
                                    'departure_time': flight_obj.get('departure_time'),
                                    'arrival_time': flight_obj.get('arrival_time'),
                                    'duration': '3h',  # Default duration
                                    'price': 'N/A USD',  # Default price
                                    'status': flight_obj.get('status'),
                                    'gate': flight_obj.get('gate'),
                                    'terminal': flight_obj.get('terminal'),
                                    'aircraft': flight_obj.get('aircraft'),
                                    'destination': flight_obj.get('destination'),
                                    'source': 'supabase'
                                })
                    else:
                        print(f"No flights found in Supabase for {origin_code}")
                except Exception as e:
                    print(f"Error fetching from Supabase: {e}")
            
        except Exception as e:
            print(f"Error reading new format JSON file: {e}")
    
    # If no data found, try reverse direction
    if not flights:
        # First try reverse old format: {destination}_to_{origin}_flights.json
        reverse_filename = f"{destination_code}_to_{origin_code}_flights.json"
        reverse_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data', reverse_filename)
        
        try:
            if os.path.exists(reverse_path):
                with open(reverse_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Check if the JSON data is a list (new format) or has schedules/prices (old format)
                if isinstance(json_data, list):
                    print(f"Found reverse JSON data: {len(json_data)} flights (new format)")
                    
                    # New format: each object is a flight with destination field
                    for flight_obj in json_data:
                        # Check if this flight matches the requested destination (origin in reverse)
                        flight_destination = flight_obj.get('destination')
                        if flight_destination == origin_code:
                            flights.append({
                                'flight_number': flight_obj.get('flight_number'),
                                'airline_name': flight_obj.get('airline'),
                                'departure_time': flight_obj.get('departure_time'),
                                'arrival_time': flight_obj.get('arrival_time'),
                                'duration': '3h',  # Default duration
                                'price': 'N/A USD',  # Default price
                                'status': flight_obj.get('status'),
                                'gate': flight_obj.get('gate'),
                                'terminal': flight_obj.get('terminal'),
                                'aircraft': flight_obj.get('aircraft'),
                                'destination': flight_obj.get('destination'),
                                'source': 'json_file_reverse_new_format'
                            })
                else:
                    # Old format: schedules and prices arrays
                    print(f"Found reverse JSON data: {len(json_data.get('schedules', []))} schedules (old format)")
                    
                    schedules = json_data.get('schedules', [])
                    prices = json_data.get('prices', [])
                    
                    for i, schedule in enumerate(schedules):
                        price_data = prices[i] if i < len(prices) else {}
                        flights.append({
                            'flight_number': schedule.get('flight_number'),
                            'airline_name': schedule.get('airline'),
                            'departure_time': schedule.get('departure_time'),
                            'arrival_time': schedule.get('arrival_time'),
                            'duration': price_data.get('duration', '3h'),
                            'price': f"{price_data.get('price', 'N/A')} {price_data.get('currency', 'USD')}",
                            'status': schedule.get('status'),
                            'gate': schedule.get('gate'),
                            'terminal': schedule.get('terminal'),
                            'aircraft': schedule.get('aircraft'),
                            'source': 'json_file_reverse_old_format'
                        })
        except Exception as e:
            print(f"Error reading reverse JSON file: {e}")
        
        # If still no data, try reverse new format: {destination}_flights.json
        if not flights:
            reverse_new_format_filename = f"{destination_code}_flights.json"
            reverse_new_format_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'data', reverse_new_format_filename)
            
            print(f"Looking for reverse new format JSON file: {reverse_new_format_path}")
            
            try:
                if os.path.exists(reverse_new_format_path):
                    with open(reverse_new_format_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    if isinstance(json_data, list):
                        print(f"Found reverse new format JSON data: {len(json_data)} flights")
                        
                        # Filter flights by destination (origin in reverse)
                        for flight_obj in json_data:
                            flight_destination = flight_obj.get('destination')
                            if flight_destination == origin_code:
                                flights.append({
                                    'flight_number': flight_obj.get('flight_number'),
                                    'airline_name': flight_obj.get('airline'),
                                    'departure_time': flight_obj.get('departure_time'),
                                    'arrival_time': flight_obj.get('arrival_time'),
                                    'duration': '3h',  # Default duration
                                    'price': 'N/A USD',  # Default price
                                    'status': flight_obj.get('status'),
                                    'gate': flight_obj.get('gate'),
                                    'terminal': flight_obj.get('terminal'),
                                    'aircraft': flight_obj.get('aircraft'),
                                    'destination': flight_obj.get('destination'),
                                    'source': 'json_file_reverse_new_format'
                                })
                    else:
                        print(f"Reverse new format file exists but is not a list: {reverse_new_format_path}")
                else:
                    print(f"Reverse new format JSON file not found: {reverse_new_format_path}")
                
            except Exception as e:
                print(f"Error reading reverse new format JSON file: {e}")
    
    print(f"Total flights found: {len(flights)}")
    return JsonResponse({'flights': flights})

# API: List all airports
class AirportListView(generics.ListAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

# API: List all flights
class FlightListView(generics.ListAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

# API: Report data (weather, air traffic, fuel, safety, constraints)
class ReportDataView(views.APIView):
    def get(self, request):
        """API endpoint to get report data from api_flight.json"""
        from .supabase_utils import load_api_flight_data
        
        # Load data from api_flight.json
        api_flight_data = load_api_flight_data()
        
        if api_flight_data:
            # Transform api_flight.json data into the expected report format
            weather_data = []
            air_traffic_data = []
            fuel_efficiency_data = []
            safety_factors_data = []
            
            for record in api_flight_data:
                # Weather data
                weather_data.append({
                    'type': record.get('conditions', 'unknown'),
                    'severity': 'Medium',
                    'visibility': f"{record.get('distance_km', 0)}km",
                    'wind_speed': f"{record.get('wind speed kmh', 0)} km/h",
                    'temperature': f"{record.get('temperature', 0)}°C",
                    'humidity': f"{record.get('humidity percent', 0)}%",
                    'pressure': f"{record.get('pressure hpa', 0)} hPa",
                    'precipitation': f"{record.get('precipitation mm', 0)} mm"
                })
                
                # Air traffic data
                air_traffic_data.append({
                    'type': f"Flight {record.get('air id', 'Unknown')}",
                    'status': record.get('alert_status', 'normal'),
                    'level': 'Medium' if record.get('alert_status') == 'warning' else 'Low',
                    'description': f"Flight monitoring for {record.get('air id', 'Unknown')}",
                    'duration': 'Continuous',
                    'altitude': f"{record.get('altitude_ft', 0)} ft",
                    'speed': f"{record.get('speed_knots', 0)} knots",
                    'heading': f"{record.get('heading_deg', 0)}°"
                })
                
                # Fuel efficiency data
                fuel_efficiency_data.append({
                    'aircraft_type': 'Commercial Aircraft',
                    'efficiency': f"{record.get('fuel_efficiency_kmpl', 0)} km/L",
                    'fuel_consumption': f"{record.get('fuel_consumption_lph', 0)} L/h",
                    'emissions': f"{record.get('fuel_flow_kgh', 0)} kg/h CO2",
                    'optimization_potential': f"{100 - record.get('engine_efficiency_percent', 0)}%",
                    'engine_rpm': record.get('engine_rpm', 0),
                    'fuel_remaining': f"{record.get('fuel_remaining_kg', 0)} kg"
                })
                
                # Safety factors data
                safety_factors_data.append({
                    'factor': f"Flight {record.get('air id', 'Unknown')} Safety",
                    'value': record.get('alert_status', 'normal'),
                    'score': f"{record.get('engine_efficiency_percent', 0)}/100",
                    'risk_level': 'Medium' if record.get('alert_status') == 'warning' else 'Low',
                    'recommendations': f"Monitor {record.get('air id', 'Unknown')} flight conditions",
                    'vibration_level': record.get('vibration_level', 0),
                    'tilt_angle': f"{record.get('tilt_angle_deg', 0)}°"
                })
            
            report_data = {
                'weather': weather_data,
                'operational_constraints': air_traffic_data,
                'fuel_efficiency': fuel_efficiency_data,
                'safety_factors': safety_factors_data
            }
            
            return Response({
                'success': True,
                'data': report_data,
                'source': 'api_flight.json',
                'count': len(api_flight_data)
            })
        else:
            return Response({
                'success': False,
                'error': 'No data available from api_flight.json',
                'source': 'none'
            }, status=404)

def api_init_supabase(request):
    """API endpoint to initialize Supabase with sample report data"""
    if request.method == 'POST':
        try:
            success = initialize_supabase_report_data()
            if success:
                return JsonResponse({'success': True, 'message': 'Supabase data initialized successfully'})
            else:
                return JsonResponse({'success': False, 'error': 'Failed to initialize Supabase data'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

def api_air_by_id(request, air_id):
    """API endpoint to fetch air traffic data by ID from Supabase"""
    try:
        air_data = fetch_air_data_by_id(air_id)
        if air_data:
            return JsonResponse({
                'success': True,
                'data': air_data,
                'source': 'supabase'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'No air record found with ID {air_id}',
                'source': 'supabase'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'supabase'
        }, status=500)

def api_weather_by_id(request, weather_id):
    """API endpoint to fetch weather data by ID from Supabase"""
    try:
        weather_data = fetch_weather_data_by_id(weather_id)
        if weather_data:
            return JsonResponse({
                'success': True,
                'data': weather_data,
                'source': 'supabase'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'No weather record found with ID {weather_id}',
                'source': 'supabase'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'supabase'
        }, status=500)

def api_fuel_by_id(request, fuel_id):
    """API endpoint to fetch fuel efficiency data by ID from Supabase"""
    try:
        fuel_data = fetch_fuel_data_by_id(fuel_id)
        if fuel_data:
            return JsonResponse({
                'success': True,
                'data': fuel_data,
                'source': 'supabase'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'No fuel record found with ID {fuel_id}',
                'source': 'supabase'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'supabase'
        }, status=500)

def api_safety_by_id(request, safety_id):
    """API endpoint to fetch safety data by ID from Supabase"""
    try:
        safety_data = fetch_safety_data_by_id(safety_id)
        if safety_data:
            return JsonResponse({
                'success': True,
                'data': safety_data,
                'source': 'supabase'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'No safety record found with ID {safety_id}',
                'source': 'supabase'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'supabase'
        }, status=500)

def api_flight_by_id(request, flight_id):
    """API endpoint to fetch flight data by ID from Supabase"""
    try:
        flight_data = fetch_flight_data_by_id(flight_id)
        if flight_data:
            return JsonResponse({
                'success': True,
                'data': flight_data,
                'source': 'supabase'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'No flight record found with ID {flight_id}',
                'source': 'supabase'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'supabase'
        }, status=500)

def api_flight_by_air_id(request, air_id):
    """API endpoint to fetch flight data by air ID from api_flight.json"""
    try:
        flight_data = fetch_flight_data_by_air_id(air_id)
        if flight_data:
            return JsonResponse({
                'success': True,
                'data': flight_data,
                'source': 'api_flight.json'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'No flight data found for air ID {air_id}',
                'source': 'api_flight.json'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'api_flight.json'
        }, status=500)

def api_all_flight_data(request):
    """API endpoint to fetch all flight data from api_flight.json"""
    try:
        flight_data = fetch_all_flight_data()
        return JsonResponse({
            'success': True,
            'data': flight_data,
            'count': len(flight_data),
            'source': 'api_flight.json'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'api_flight.json'
        }, status=500)

def api_flight_by_condition(request, condition):
    """API endpoint to fetch flight data by weather condition"""
    try:
        flight_data = fetch_flight_data_by_condition(condition)
        return JsonResponse({
            'success': True,
            'data': flight_data,
            'count': len(flight_data),
            'condition': condition,
            'source': 'api_flight.json'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'api_flight.json'
        }, status=500)

def api_flight_by_alert_status(request, alert_status):
    """API endpoint to fetch flight data by alert status"""
    try:
        flight_data = fetch_flight_data_by_alert_status(alert_status)
        return JsonResponse({
            'success': True,
            'data': flight_data,
            'count': len(flight_data),
            'alert_status': alert_status,
            'source': 'api_flight.json'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'api_flight.json'
        }, status=500)

def api_available_air_ids(request):
    """API endpoint to get all available air IDs"""
    try:
        air_ids = get_available_air_ids()
        return JsonResponse({
            'success': True,
            'data': air_ids,
            'count': len(air_ids),
            'source': 'api_flight.json'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'api_flight.json'
        }, status=500)

def api_available_conditions(request):
    """API endpoint to get all available weather conditions"""
    try:
        conditions = get_available_conditions()
        return JsonResponse({
            'success': True,
            'data': conditions,
            'count': len(conditions),
            'source': 'api_flight.json'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'api_flight.json'
        }, status=500)

def api_available_alert_statuses(request):
    """API endpoint to get all available alert statuses"""
    try:
        alert_statuses = get_available_alert_statuses()
        return JsonResponse({
            'success': True,
            'data': alert_statuses,
            'count': len(alert_statuses),
            'source': 'api_flight.json'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'api_flight.json'
        }, status=500)

def api_upload_flight_data_to_supabase(request):
    """API endpoint to upload api_flight.json data to Supabase"""
    if request.method == 'POST':
        try:
            success = upload_api_flight_data_to_supabase()
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Flight data uploaded to Supabase successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to upload flight data to Supabase'
                }, status=500)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    else:
        return JsonResponse({
            'error': 'Only POST method allowed'
        }, status=405)

def api_flight_data_for_optimize(request):
    """API endpoint to fetch flight data for the optimize page"""
    air_id = request.GET.get('air_id')
    condition = request.GET.get('condition')
    alert_status = request.GET.get('alert_status')
    
    try:
        if air_id:
            # Fetch specific air ID
            flight_data = fetch_flight_data_by_air_id(air_id)
            if flight_data:
                return JsonResponse({
                    'success': True,
                    'data': [flight_data],
                    'count': 1,
                    'source': 'api_flight.json'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'No flight data found for air ID {air_id}',
                    'source': 'api_flight.json'
                }, status=404)
        
        elif condition:
            # Fetch by condition
            flight_data = fetch_flight_data_by_condition(condition)
            return JsonResponse({
                'success': True,
                'data': flight_data,
                'count': len(flight_data),
                'condition': condition,
                'source': 'api_flight.json'
            })
        
        elif alert_status:
            # Fetch by alert status
            flight_data = fetch_flight_data_by_alert_status(alert_status)
            return JsonResponse({
                'success': True,
                'data': flight_data,
                'count': len(flight_data),
                'alert_status': alert_status,
                'source': 'api_flight.json'
            })
        
        else:
            # Return all data
            flight_data = fetch_all_flight_data()
            return JsonResponse({
                'success': True,
                'data': flight_data,
                'count': len(flight_data),
                'source': 'api_flight.json'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'source': 'api_flight.json'
        }, status=500)

def debug_api_flight_data(request):
    """Debug view to test api_flight.json data loading"""
    from .supabase_utils import load_api_flight_data, get_available_air_ids, get_available_conditions, get_available_alert_statuses
    
    api_flight_data = load_api_flight_data()
    available_air_ids = get_available_air_ids()
    available_conditions = get_available_conditions()
    available_alert_statuses = get_available_alert_statuses()
    
    debug_info = {
        'data_loaded': len(api_flight_data) if api_flight_data else 0,
        'sample_record': api_flight_data[0] if api_flight_data else None,
        'available_air_ids': available_air_ids,
        'available_conditions': available_conditions,
        'available_alert_statuses': available_alert_statuses,
        'data_source': 'api_flight' if api_flight_data else 'none'
    }
    
    return JsonResponse(debug_info)

from django.shortcuts import render

def chat_bot(request):
    return render(request, 'chat_bot.html')

@csrf_exempt
def chat_gemini_api(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        user_message = data.get("message", "")
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            return JsonResponse({"error": "Gemini API key not set."}, status=500)
        # Call Gemini API (replace with actual endpoint and payload as needed)
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + gemini_api_key
        payload = {
            "contents": [{"parts": [{"text": user_message}]}]
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                # Extract the AI's response text
                ai_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response from Gemini.")
                return JsonResponse({"response": ai_text})
            else:
                return JsonResponse({"error": f"Gemini API error: {response.text}"}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST only"}, status=405)

@csrf_exempt
def api_ask_ai(request):
    """API endpoint to summarize report data and suggest efficiency improvements."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # The data may be wrapped as {card: ..., data: {...}} or just {...}
            report = data.get('data', data)
            summary = []
            suggestions = []

            # Summarize fuel efficiency
            fuel_eff = report.get('fuel_efficiency', [])
            if fuel_eff:
                for entry in fuel_eff:
                    summary.append(
                        f"Aircraft type: {entry.get('aircraft_type', 'N/A')}, "
                        f"Efficiency: {entry.get('efficiency', 'N/A')}, "
                        f"Fuel Consumption: {entry.get('fuel_consumption', 'N/A')}, "
                        f"Emissions: {entry.get('emissions', 'N/A')}"
                    )
                    # Suggestion logic
                    try:
                        eff_val = float(str(entry.get('efficiency', '0')).split()[0])
                    except Exception:
                        eff_val = 0
                    if eff_val < 20:
                        suggestions.append("Consider reducing aircraft weight, optimizing cruise speed, improving engine maintenance, or using more efficient flight paths to increase fuel efficiency.")
                    else:
                        suggestions.append("Fuel efficiency is good. Maintain current operational practices.")
            else:
                summary.append("No fuel efficiency data found.")
                suggestions.append("No suggestions available for fuel efficiency.")

            # Optionally, add summaries for other sections (weather, safety, etc.)
            # ...

            return JsonResponse({
                "summary": "\n".join(summary),
                "suggestions": "\n".join(suggestions)
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=405)

# QAOA Angle Predictor Model
model = None

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'qaoa_angle_predictor.keras')

def get_model():
    global model
    if model is None:
        model = tf.keras.models.load_model(MODEL_PATH)
    return model

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class QAOAPredictView(APIView):
    def post(self, request, *args, **kwargs):
        # CORS headers
        response_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        try:
            data = request.data
            qubo_matrix = data.get('qubo_matrix')
            if qubo_matrix is None:
                return Response({'error': 'Missing qubo_matrix'}, status=400, headers=response_headers)
            arr = np.array(qubo_matrix, dtype=np.float32)
            if arr.shape != (8, 8):
                return Response({'error': 'qubo_matrix must be 8x8'}, status=400, headers=response_headers)
            arr = arr.flatten().reshape(1, -1)
            prediction = model.predict(arr)
            # Assume model outputs [beta, gamma] as a 2-element array
            beta, gamma = float(prediction[0][0]), float(prediction[0][1])
            return Response({'beta': beta, 'gamma': gamma}, headers=response_headers)
        except Exception as e:
            return Response({'error': str(e)}, status=500, headers=response_headers)
    
    def options(self, request, *args, **kwargs):
        # Handle preflight CORS
        response = Response(status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

