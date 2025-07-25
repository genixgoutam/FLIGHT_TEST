from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Airport, AircraftProfile, OperationalConstraint
import json
import math
import numpy as np
from datetime import datetime
from django.utils.timezone import now
from django.core.cache import cache

# Aircraft metrics functions for safety factors
def compute_tilt_angle(velocity, vertical_rate):
    """Calculate aircraft tilt angle from velocity and vertical rate"""
    if velocity == 0:
        return 90.0 if vertical_rate > 0 else -90.0
    angle_rad = np.arctan2(vertical_rate, velocity)
    angle_deg = round(angle_rad * 180 / np.pi, 2)
    return angle_deg

def fetch_aircraft_metrics():
    """Fetch real-time aircraft metrics from OpenSky Network API"""
    # Try multiple approaches to get aircraft data
    urls_to_try = [
        "https://opensky-network.org/api/states/all",  # General query
        "https://opensky-network.org/api/states/all?icao24=60006b",  # Specific aircraft
        "https://opensky-network.org/api/states/all?lamin=12&lomin=77&lamax=13&lomax=78"
    ]
    
    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data and data.get("states") and len(data["states"]) > 0:
                        # Use first available aircraft or find our specific one
                        target_state = None
                        
                        for state in data["states"]:
                            if state[0] == "60006b":  # Our specific aircraft
                                target_state = state
                                break
                        
                        # If specific aircraft not found, use first available
                        if not target_state and len(data["states"]) > 0:
                            target_state = data["states"][0]
                        
                        if target_state:
                            velocity = target_state[9] if target_state[9] is not None else 0
                            vertical_rate = target_state[11] if target_state[11] is not None else 0
                            
                            # Calculate vibration level
                            vibration = round(np.std([velocity, vertical_rate]), 2) if velocity != 0 or vertical_rate != 0 else 0
                            
                            # Calculate tilt angle
                            tilt_angle = compute_tilt_angle(velocity, vertical_rate)
                            
                            aircraft_id = target_state[0] or "Unknown"
                            source_text = f"Real-time OpenSky data (Aircraft: {aircraft_id})"
                            
                            return [
                                {
                                    "factor": "Vibration Level",
                                    "value": f"{vibration} m/s",
                                    "score": round(vibration * 2, 2),
                                    "risk_level": "High" if vibration > 2 else "Medium" if vibration > 1 else "Low",
                                    "recommendation": "Inspect airframe for stress" if vibration > 2 else "Monitor vibration levels",
                                    "source": source_text
                                },
                                {
                                    "factor": "Tilt Angle",
                                    "value": f"{tilt_angle}°",
                                    "score": round(abs(tilt_angle) / 10, 2),
                                    "risk_level": "High" if abs(tilt_angle) > 30 else "Medium" if abs(tilt_angle) > 15 else "Low",
                                    "recommendation": "Check for abnormal climb/descent" if abs(tilt_angle) > 15 else "Normal flight attitude",
                                    "source": source_text
                                },
                                {
                                    "factor": "Ground Speed",
                                    "value": f"{velocity} m/s" if velocity else "N/A",
                                    "score": 0,
                                    "risk_level": "Low",
                                    "recommendation": "Speed within normal parameters",
                                    "source": source_text
                                },
                                {
                                    "factor": "Vertical Rate",
                                    "value": f"{vertical_rate} m/s" if vertical_rate else "N/A",
                                    "score": 0,
                                    "risk_level": "Low", 
                                    "recommendation": "Vertical movement normal",
                                    "source": source_text
                                }
                            ]
                            
                except json.JSONDecodeError:
                    continue  # Try next URL
                    
        except requests.RequestException:
            continue  # Try next URL
    
    # If all URLs failed, return simulated data
    return generate_simulated_safety_metrics("OpenSky API unavailable - using realistic simulation")

def generate_simulated_safety_metrics(reason="Simulation"):
    """Generate simulated safety metrics when real data is unavailable"""
    import random
    
    # Generate realistic simulated values for Boeing 747SR
    velocity = round(random.uniform(220, 280), 1)  # Boeing 747 cruise speed range
    vertical_rate = round(random.uniform(-3, 3), 1)  # Normal vertical movements
    
    # Calculate realistic vibration based on aircraft type
    base_vibration = random.uniform(0.3, 0.8)  # Low baseline for commercial aircraft
    vibration = round(base_vibration, 2)
    
    # Calculate tilt angle
    tilt_angle = compute_tilt_angle(velocity, vertical_rate)
    
    return [
        {
            "factor": "Vibration Level",
            "value": f"{vibration} m/s",
            "score": round(vibration * 2, 2),
            "risk_level": "High" if vibration > 2 else "Medium" if vibration > 1 else "Low",
            "recommendation": "Inspect airframe for stress" if vibration > 2 else "Monitor vibration levels" if vibration > 0.5 else "Vibration within normal limits",
            "source": f"Boeing 747SR simulation - {reason}"
        },
        {
            "factor": "Tilt Angle",
            "value": f"{tilt_angle}°",
            "score": round(abs(tilt_angle) / 10, 2),
            "risk_level": "High" if abs(tilt_angle) > 30 else "Medium" if abs(tilt_angle) > 15 else "Low",
            "recommendation": "Check for abnormal climb/descent" if abs(tilt_angle) > 15 else "Normal flight attitude",
            "source": f"Boeing 747SR simulation - {reason}"
        },
        {
            "factor": "Ground Speed",
            "value": f"{velocity} m/s ({round(velocity * 1.944, 1)} knots)",
            "score": 0,
            "risk_level": "Low",
            "recommendation": "Speed within normal cruise parameters",
            "source": f"Boeing 747SR simulation - {reason}"
        },
        {
            "factor": "Vertical Rate",
            "value": f"{vertical_rate} m/s ({round(vertical_rate * 196.85, 0)} ft/min)",
            "score": 0,
            "risk_level": "Low", 
            "recommendation": "Vertical movement normal",
            "source": f"Boeing 747SR simulation - {reason}"
        }
    ]

def fetch_operational_constraints(hex_code="60006B"):
    """Fetch operational constraints for a specific aircraft"""
    try:
        # Make hex_code lookup case-insensitive
        aircraft = AircraftProfile.objects.get(hex_code__iexact=hex_code)
        constraints = OperationalConstraint.objects.filter(aircraft=aircraft)
        
        if constraints.exists():
            constraints_data = {
                "aircraft_info": {
                    "hex_code": aircraft.hex_code,
                    "type": aircraft.type,
                    "operator": aircraft.operator,
                    "registration": aircraft.registration,
                    "country": aircraft.country
                },
                "constraints": []
            }
            
            # Group constraints by category for better organization
            weight_constraints = []
            runway_constraints = []
            performance_constraints = []
            maintenance_constraints = []
            other_constraints = []
            
            for constraint in constraints:
                constraint_data = {
                    "type": constraint.constraint_type,
                    "value": constraint.value,
                    "unit": constraint.unit,
                    "notes": constraint.notes,
                    "formatted_value": f"{constraint.value} {constraint.unit}"
                }
                
                # Categorize constraints
                if "Weight" in constraint.constraint_type:
                    weight_constraints.append(constraint_data)
                elif "Runway" in constraint.constraint_type:
                    runway_constraints.append(constraint_data)
                elif any(term in constraint.constraint_type for term in ["Speed", "Ceiling", "Range", "Fuel"]):
                    performance_constraints.append(constraint_data)
                elif "Maintenance" in constraint.constraint_type:
                    maintenance_constraints.append(constraint_data)
                else:
                    other_constraints.append(constraint_data)
            
            # Add categorized constraints
            if weight_constraints:
                constraints_data["constraints"].append({
                    "category": "Weight Limitations",
                    "items": weight_constraints
                })
            
            if runway_constraints:
                constraints_data["constraints"].append({
                    "category": "Runway Requirements",
                    "items": runway_constraints
                })
            
            if performance_constraints:
                constraints_data["constraints"].append({
                    "category": "Performance Specifications",
                    "items": performance_constraints
                })
            
            if maintenance_constraints:
                constraints_data["constraints"].append({
                    "category": "Maintenance Schedule",
                    "items": maintenance_constraints
                })
            
            if other_constraints:
                constraints_data["constraints"].append({
                    "category": "Other Constraints",
                    "items": other_constraints
                })
            
            return constraints_data
        else:
            return {"error": f"No operational constraints found for aircraft {hex_code}"}
            
    except AircraftProfile.DoesNotExist:
        return {"error": f"Aircraft profile not found for hex code {hex_code}"}
    except Exception as e:
        return {"error": f"Failed to fetch operational constraints: {str(e)}"}


# Aircraft Configuration - Constant ICAO Code
DEFAULT_AIRCRAFT_ICAO = '60006B'  # Boeing 747SR (uppercase to match database)

# Load airport data
data_load = 'airports_cleaned.json'
try:
    with open(data_load, 'r', encoding='utf-8') as file:
        data = json.load(file)
except FileNotFoundError:
    data = []
# Main report view
def report(request):
    major_airports = [airport.get('code') for airport in data if airport.get('code') ]
    airports = Airport.objects.filter(code__in=major_airports).order_by('name')
    if not airports.exists():
        airports = Airport.objects.all().order_by('name')[:100]
    return render(request, 'report.html', {'airports': airports})

AIRPORT_COORDINATES = {
    airport['code']: {
        'latitude': airport['latitude'],
        'longitude': airport['longitude'],
        'name': airport['name']
    }
    for airport in data
    if airport.get('code') and airport.get('latitude') and airport.get('longitude')
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    # Earth radius in kilometers
    R = 6371.0
    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    # Haversine formula
    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Distance in kilometers
    distance = R * c
    return round(distance, 2)

def calculate_distance(origin_code, destination_code):
    """Calculate distance between two airports using Haversine formula"""
    try:
        # Fetch airport coordinates from database
        origin_airport = Airport.objects.get(code=origin_code)
        destination_airport = Airport.objects.get(code=destination_code)
        
        # Check if coordinates are available
        if (origin_airport.latitude is None or origin_airport.longitude is None or
            destination_airport.latitude is None or destination_airport.longitude is None):
            # Fallback to hardcoded coordinates if database doesn't have them
            if origin_code in AIRPORT_COORDINATES and destination_code in AIRPORT_COORDINATES:
                origin = AIRPORT_COORDINATES[origin_code]
                destination = AIRPORT_COORDINATES[destination_code]
                distance_km = haversine_distance(
                    origin['latitude'], origin['longitude'],
                    destination['latitude'], destination['longitude']
                )
                distance_miles = round(distance_km * 0.621371, 2)
                return {
                    'distance_km': distance_km,
                    'distance_miles': distance_miles,
                    'origin': f"{origin['name']} ({origin_code})",
                    'destination': f"{destination['name']} ({destination_code})"
                }
            else:
                return None
        
        # Use database coordinates
        distance_km = haversine_distance(
            origin_airport.latitude, origin_airport.longitude,
            destination_airport.latitude, destination_airport.longitude
        )
        
        # Convert to miles (1 km = 0.621371 miles)
        distance_miles = round(distance_km * 0.621371, 2)
        
        return {
            'distance_km': distance_km,
            'distance_miles': distance_miles,
            'origin': f"{origin_airport.name} ({origin_code})",
            'destination': f"{destination_airport.name} ({destination_code})"
        }
        
    except Airport.DoesNotExist:
        # Fallback to hardcoded coordinates if airports not found in database
        if origin_code in AIRPORT_COORDINATES and destination_code in AIRPORT_COORDINATES:
            origin = AIRPORT_COORDINATES[origin_code]
            destination = AIRPORT_COORDINATES[destination_code]
            distance_km = haversine_distance(
                origin['latitude'], origin['longitude'],
                destination['latitude'], destination['longitude']
            )
            distance_miles = round(distance_km * 0.621371, 2)
            return {
                'distance_km': distance_km,
                'distance_miles': distance_miles,
                'origin': f"{origin['name']} ({origin_code})",
                'destination': f"{destination['name']} ({destination_code})"
            }
        return None



# Weather forecast function using Open-Meteo API
def fetch_forecast(place):
    """Fetch weather forecast for a given airport code using Open-Meteo API"""
    if not place:
        return [{"error": "Airport code is missing."}]
    
    # Get coordinates for the airport
    airport_code = place.upper()
    if airport_code not in AIRPORT_COORDINATES:
        return [{"error": f"Airport code {airport_code} not supported. Supported: {', '.join(AIRPORT_COORDINATES.keys())}"}]
    
    coords = AIRPORT_COORDINATES[airport_code]
    latitude = coords['latitude']
    longitude = coords['longitude']
    airport_name = coords['name']
    
    # Open-Meteo API URL - Only fetch current weather data
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m,wind_direction_10m,relative_humidity_2m,surface_pressure,visibility,precipitation,weather_code&timezone=auto"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract current weather data only
            current = data.get('current', {})
            
            # Format current time properly
            current_time = current.get('time', 'N/A')
            if current_time != 'N/A':
                # Convert ISO format to readable format
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                    current_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            # Weather code descriptions
            weather_codes = {
                0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
                55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain",
                67: "Heavy freezing rain", 71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
                77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
                82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
                95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
            }
            
            weather_code = current.get('weather_code', 0)
            weather_description = weather_codes.get(weather_code, "Unknown")
            
            # Only return current weather data
            current_weather = {
                "time": current_time,
                "location": f"{airport_name} ({airport_code})",
                "temperature": f"{current.get('temperature_2m', 'N/A')}°C",
                "humidity": f"{current.get('relative_humidity_2m', 'N/A')}%",
                "pressure": f"{current.get('surface_pressure', 'N/A')} hPa",
                "wind_speed": f"{current.get('wind_speed_10m', 'N/A')} m/s",
                "wind_direction": f"{current.get('wind_direction_10m', 'N/A')}°",
                "visibility": f"{current.get('visibility', 'N/A')} m",
                "precipitation": f"{current.get('precipitation', 0)} mm",
                "weather_condition": weather_description,
                "weather_code": weather_code,
                "type": "current"
            }
            
            return [current_weather]  # Return only current weather
            
        else:
            return [{"error": f"Open-Meteo API Error {response.status_code}: {response.text[:300]}"}]
            
    except Exception as e:
        return [{"error": f"Weather fetch failed: {str(e)}"}]

# Fuel efficiency function
def fetch_fuel_efficiency(aircraft_code, distance_miles):
    """Fetch fuel efficiency data for given aircraft and distance"""
    if not aircraft_code or distance_miles <= 0:
        return {"error": "Missing or invalid parameters."}
    
    # Try external API first
    distance_nm = round(distance_miles / 1.15078, 2)
    url = f"https://despouy.ca/flight-fuel-api/q/?aircraft={aircraft_code}&distance={distance_nm}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                record = data[0]
                # Check if we have meaningful data
                if record.get("model") or record.get("fuel"):
                    result = {}
                    if record.get("model"):
                        result["aircraft_type"] = record["model"]
                    if record.get("fuel"):
                        result["fuel_consumption"] = f"{record['fuel']} kg"
                    if record.get("co2"):
                        result["emissions"] = f"{record['co2']} kg CO₂"
                    if record.get("distance"):
                        result["distance"] = f"{record['distance']} NM"
                    if record.get("icao"):
                        result["icao_code"] = record["icao"]
                    if record.get("iata"):
                        result["code"] = record["iata"]
                    return result
    except Exception as e:
        pass  # Fall through to Boeing 747SR specifications
    
    # Fallback to Boeing 747SR specifications
    return generate_boeing_747sr_fuel_data(distance_miles)

def generate_boeing_747sr_fuel_data(distance_miles):
    """Generate Boeing 747SR fuel efficiency data based on specifications"""
    # Boeing 747SR fuel consumption: approximately 4.5 kg/km
    distance_km = distance_miles * 1.60934
    
    # Calculate fuel consumption
    fuel_consumption_kg = round(distance_km * 4.5, 1)
    
    # Calculate CO2 emissions (approximately 3.15 kg CO2 per kg of fuel)
    co2_emissions_kg = round(fuel_consumption_kg * 3.15, 1)
    
    # Convert to nautical miles for consistency
    distance_nm = round(distance_miles / 1.15078, 1)
    
    return {
        "aircraft_type": "Boeing 747SR-81 (SF)",
        "fuel_consumption": f"{fuel_consumption_kg} kg",
        "emissions": f"{co2_emissions_kg} kg CO₂",
        "distance": f"{distance_nm} NM ({distance_miles} miles)",
        "icao_code": "60006B",
        "code": "EK-74711",
        "fuel_efficiency": f"{round(fuel_consumption_kg/distance_km, 2)} kg/km",
        "source": "Boeing 747SR specifications",
        "notes": "Calculated based on Boeing 747SR-81 performance data"
    }

# Route data function

def get_route_data(origin, destination):
    """Get route data between two airports"""
    try:
        distance_info = calculate_distance(origin, destination)
        if distance_info:
            return {
                "greatCircleDistance": {"km": distance_info['distance_km']},
                "realisticFlightTime": {
                    "h": round(distance_info['distance_km'] / 850, 1),  # Assume 850 km/h cruise speed
                    "averageSpeedKph": 850
                },
                "origin": distance_info['origin'],
                "destination": distance_info['destination']
            }
        else:
            return {"error": "Unable to calculate route data"}
    except Exception as e:
        return {"error": f"Route data calculation failed: {str(e)}"}

def simulate_safety_report(origin, destination, route_data):
    """Generate safety report based on route data"""
    if "error" in route_data:
        return route_data
    
    distance = route_data.get("greatCircleDistance", {}).get("km", 5000)
    time = route_data.get("realisticFlightTime", {}).get("h")
    speed = route_data.get("realisticFlightTime", {}).get("averageSpeedKph")
    
    # Fallback calculations
    if not time and distance:
        speed = 850  # Assume typical cruise speed
        time = round(distance / speed, 1)
    if not speed and time:
        speed = round(distance / time, 1)
    
    # Simulated safety values
    aircraft_age = 8
    engine_count = 2
    alert_status = "normal"
    engine_efficiency = round(max(0, 100 - aircraft_age * 2.6), 1)
    vibration_level = round(engine_count * 0.7, 2)
    tilt_angle = round(engine_count * 3.5, 1)
    aircraft_model = "Airbus A330 (simulated)"
    
    return {
        "factor": f"Flight {origin} → {destination} Safety",
        "value": alert_status,
        "score": f"{engine_efficiency}/100",
        "risk_level": "Low",
        "recommendations": f"Monitor weather and runway conditions at {origin} and {destination}",
        "vibration_level": vibration_level,
        "tilt_angle": f"{tilt_angle}°",
        "aircraft_model": aircraft_model,
        "distance": f"{distance} km",
        "estimated_time": f"{time} hours",
        "cruising_speed": f"{speed} km/h"
    }

@csrf_exempt
def search_airports(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'airports': []})
    airports = Airport.objects.filter(
        Q(code__icontains=query) |
        Q(city__icontains=query) |
        Q(country__icontains=query) |
        Q(name__icontains=query)
    ).order_by('code')[:50]
    airport_list = []
    for airport in airports:
        airport_list.append({
            'code': airport.code,
            'name': airport.name,
            'city': airport.city,
            'country': airport.country,
            'display_text': f"{airport.country}, {airport.city} ({airport.code}) - {airport.name}"
        })
    return JsonResponse({'airports': airport_list})

@csrf_exempt
def safety_report_view(request):
    origin = request.POST.get("origin", "").upper().strip()
    destination = request.POST.get("destination", "").upper().strip()
    
    if not origin or not destination:
        return JsonResponse({"error": "Origin and destination are required."}, status=400)
    
    # Get route data
    route_data = get_route_data(origin, destination)
    
    # Generate safety report
    if "error" not in route_data:
        safety_report = simulate_safety_report(origin, destination, route_data)

def get_fuel_efficiency(request):
    # Always use constant aircraft ICAO code, ignore any provided aircraft_code
    try:
        distance_miles = float(request.GET.get("distance_miles", "0").strip())
    except ValueError:
        return JsonResponse({"error": "Invalid distance value."}, status=400)
    
    # Use the constant aircraft ICAO code
    result = fetch_fuel_efficiency(DEFAULT_AIRCRAFT_ICAO, distance_miles)
    
    if "error" in result:
        return JsonResponse(result, status=400)
    else:
        return JsonResponse(result)

@csrf_exempt
def get_forecast(request):
    city1 = request.GET.get("city1", "").strip()
    city2 = request.GET.get("city2", "").strip()
    result = {}
    for city in [city1, city2]:
        if city:
            result[city] = fetch_forecast(city)
        else:
            result[city] = [{"error": "City name is missing."}]
    return JsonResponse(result)

