from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.http import require_http_methods
from .models import Airport, Flight
from .api_utils import (
    haversine_distance, get_forecast, get_fuel_efficiency, safety_report_view, search_airports,
    simulate_safety_report, get_route_data, generate_boeing_747sr_fuel_data, fetch_fuel_efficiency,
    fetch_forecast, calculate_distance, fetch_aircraft_metrics, fetch_operational_constraints,
    DEFAULT_AIRCRAFT_ICAO, AIRPORT_COORDINATES
)
from rest_framework.views import APIView
import json
import os
import math 
from django.utils.decorators import method_decorator
import numpy as np
import tensorflow as tf
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, LineString
import folium
from folium.plugins import MeasureControl

# API endpoint for all airports
@csrf_exempt
def api_airports(request):
    if request.method == 'GET':
        from .models import Airport
        airports = Airport.objects.all()
        data = []
        for airport in airports:
            data.append({
                'id': airport.id,
                'name': airport.name,
                'code': airport.code,
                'city': airport.city,
                'country': airport.country,
                'latitude': airport.latitude,
                'longitude': airport.longitude
            })
        return JsonResponse(data, safe=False)


# API endpoint to return 3 routes: QAOA, Dijkstra, Alternative
@api_view(['GET'])
def api_flights(request):
    # Example: Replace with actual route generation logic
    # Each route should have: method, coordinates, origin_name, destination_name
    routes = [
        {
            'method': 'QAOA',
            'coordinates': [[20, 0], [25, 10], [30, 20]],
            'origin_name': 'Origin Airport',
            'destination_name': 'Destination Airport',
        },
        {
            'method': 'Dijkstra',
            'coordinates': [[20, 0], [22, 5], [30, 20]],
            'origin_name': 'Origin Airport',
            'destination_name': 'Destination Airport',
        },
        {
            'method': 'Alternative',
            'coordinates': [[20, 0], [18, -5], [30, 20]],
            'origin_name': 'Origin Airport',
            'destination_name': 'Destination Airport',
        },
    ]
    return Response(routes)

def calculate_route_distance(route_coordinates):
    """Calculate total distance for a route"""
    total_distance = 0
    for i in range(len(route_coordinates) - 1):
        lat1, lon1 = route_coordinates[i]
        lat2, lon2 = route_coordinates[i + 1]
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        total_distance += distance
    return total_distance

def api_stops(request):
    stops = list(Airport.objects.all().values('code', 'name', 'latitude', 'longitude', 'country'))
    return JsonResponse({'stops': stops})

def estimate_flight_time(distance_km, avg_speed_kmh=800):
    """Estimate flight time based on distance and average speed"""
    time_hours = (distance_km / avg_speed_kmh) + 0.5
    hours = int(time_hours)
    minutes = int((time_hours - hours) * 60)
    return hours, minutes

def calculate_fuel_cost(distance_km, fuel_price_per_liter=0.8, fuel_consumption_lph=2500):
    """Calculate fuel cost based on distance and fuel consumption"""
    flight_hours = distance_km / 800
    fuel_consumed = flight_hours * fuel_consumption_lph
    fuel_cost = fuel_consumed * fuel_price_per_liter
    return fuel_cost

def calculate_total_cost(distance_km, base_cost_per_km=1.2):
    """Calculate total operational cost including fuel, maintenance, crew, etc."""
    fuel_cost = calculate_fuel_cost(distance_km)
    operational_cost = distance_km * base_cost_per_km
    total_cost = fuel_cost + operational_cost
    return total_cost, fuel_cost

AIRPORTS_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'airports_cleaned.json')
with open(AIRPORTS_JSON_PATH, 'r', encoding='utf-8') as f:
    AIRPORTS = json.load(f)
AIRPORT_CODES = [a['code'] for a in AIRPORTS]

DIST_MATRIX = {}
for a in AIRPORTS:
    for b in AIRPORTS:
        if a['code'] != b['code']:
            dist = math.sqrt((a['latitude'] - b['latitude']) ** 2 + (a['longitude'] - b['longitude']) ** 2)
            DIST_MATRIX[(a['code'], b['code'])] = dist

def home(request):
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
    return [start, end]

def find_alternatives(main_path, codes):
    alternatives = []
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

        qubo_matrix = [[0]*8 for _ in range(8)]
        api_url = 'http://127.0.0.1:8000/api/qaoa-predict/'
        try:
            qaoa_response = requests.post(api_url, json={'qubo_matrix': qubo_matrix})
            qaoa_result = qaoa_response.json()
        except Exception as e:
            qaoa_result = {'error': str(e)}
        main_path = dijkstra(origin, destination, AIRPORT_CODES, DIST_MATRIX)
        alt_paths = find_alternatives(main_path, AIRPORT_CODES)
        airport_dict = {a['code']: a for a in AIRPORTS}
        def build_route_obj(codes):
            coords = [[airport_dict[code]['latitude'], airport_dict[code]['longitude']] for code in codes if code in airport_dict]
            path = ' → '.join(codes)
            return {'coordinates': coords, 'path': path}
        all_routes = [build_route_obj(main_path)] + [build_route_obj(alt) for alt in alt_paths]

        main_route = all_routes[0] if all_routes else None
        if main_route and main_route['coordinates']:
            total_distance_km = calculate_route_distance(main_route['coordinates'])
            total_distance_miles = total_distance_km * 0.621371
            hours, minutes = estimate_flight_time(total_distance_km)
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
    airports = Airport.objects.all()
    airlines = Flight.objects.values_list('airline', flat=True).distinct().order_by('airline')
    return render(request, 'choices.html', {
        'airports': airports,
        'airlines': airlines
    })

def map_view(request):
    return render(request, 'map.html')

def api_airports(request):
    airports = list(Airport.objects.all().values('code', 'name', 'latitude', 'longitude'))
    return JsonResponse({"airports": airports})

def api_stops(request):
    stops = list(Airport.objects.all().values('code', 'name', 'latitude', 'longitude', 'country'))
    return JsonResponse({'stops': stops})

def api_all_airports(request):
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

def chat_bot(request):
    return render(request, 'chat_bot.html')

@csrf_exempt
def chat_gemini_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            return JsonResponse({"error": "Gemini API key not set."}, status=500)
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + gemini_api_key
        payload = {
            "contents": [{"parts": [{"text": user_message}]}]
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                ai_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response from Gemini.")
                return JsonResponse({"response": ai_text})
            else:
                return JsonResponse({"error": f"Gemini API error: {response.text}"}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST only"}, status=405)

@csrf_exempt
def api_ask_ai(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report = data.get('data', data)
            summary = []
            suggestions = []
            fuel_eff = report.get('fuel_efficiency', [])
            if fuel_eff:
                for entry in fuel_eff:
                    summary.append(
                        f"Aircraft type: {entry.get('aircraft_type', 'N/A')}, "
                        f"Efficiency: {entry.get('efficiency', 'N/A')}, "
                        f"Fuel Consumption: {entry.get('fuel_consumption', 'N/A')}, "
                        f"Emissions: {entry.get('emissions', 'N/A')}"
                    )
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
            return JsonResponse({
                "summary": "\n".join(summary),
                "suggestions": "\n".join(suggestions)
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=405)

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
        from rest_framework.response import Response
        global model
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
            if model is None:
                # Load the model if not loaded
                import tensorflow as tf
                model = tf.keras.models.load_model('qaoa_angle_predictor.keras')
            prediction = model.predict(arr)
            beta, gamma = float(prediction[0][0]), float(prediction[0][1])
            return Response({'beta': beta, 'gamma': gamma}, headers=response_headers)
        except Exception as e:
            return Response({'error': str(e)}, status=500, headers=response_headers)
    
    def options(self, request, *args, **kwargs):
        response = requests.Response(status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

from django.shortcuts import render
from .models import Airport

def report(request):
    origin = request.GET.get('origin', '').strip().upper()
    destination = request.GET.get('destination', '').strip().upper()
    airports = Airport.objects.all().order_by('name')
    if not origin or not destination:
        # Render a form or selection page if parameters are missing
        return render(request, 'report.html', {'airports': airports})
    # If both parameters are present, proceed with your report logic
    # ...existing report logic...
    return render(request, 'report.html', {
        'airports': airports,
        'origin': origin,
        'destination': destination,
        # Add other context variables as needed
    })
@csrf_exempt
def full_report(request):
    """
    Comprehensive flight report fetching all data at once
    Supports both GET and POST methods
    """
    if request.method == 'POST':
        origin = request.POST.get('origin', '').strip().upper()
        destination = request.POST.get('destination', '').strip().upper()
    else:
        origin = request.GET.get('origin', '').strip().upper()
        destination = request.GET.get('destination', '').strip().upper()
    
    if not origin or not destination:
        return JsonResponse({"error": "Origin and destination are required."}, status=400)
    
    distance_info = calculate_distance(origin, destination)
    if distance_info is None:
        return JsonResponse({"error": f"Unsupported airport codes. Supported: {', '.join(AIRPORT_COORDINATES.keys())}"}, status=400)
    
    distance_miles = distance_info['distance_miles']
    distance_km = distance_info['distance_km']

    try:
        origin_weather = fetch_forecast(origin)
        destination_weather = fetch_forecast(destination)
        weather_data = {
            'origin': {'city': origin, 'forecast': origin_weather},
            'destination': {'city': destination, 'forecast': destination_weather}
        }
    except Exception as e:
        weather_data = {"error": f"Weather fetch failed: {str(e)}"}

    if distance_miles > 0:
        try:
            fuel_efficiency = fetch_fuel_efficiency(DEFAULT_AIRCRAFT_ICAO, distance_miles)
        except Exception as e:
            fuel_efficiency = {"error": f"Fuel efficiency fetch failed: {str(e)}"}
    else:
        fuel_efficiency = {"error": "Distance required for fuel efficiency calculation"}

    try:
        safety_factors = fetch_aircraft_metrics()
        if isinstance(safety_factors, list) and len(safety_factors) > 0:
            if "error" in safety_factors[0]:
                safety_factors = {"error": safety_factors[0]["error"]}
            else:
                safety_factors = {"factors": safety_factors}
        route_data = get_route_data(origin, destination)
    except Exception as e:
        safety_factors = {"error": f"Safety factors fetch failed: {str(e)}"}
        route_data = {"error": f"Route data fetch failed: {str(e)}"}

    try:
        operational_constraints = fetch_operational_constraints(DEFAULT_AIRCRAFT_ICAO)
    except Exception as e:
        operational_constraints = {"error": f"Operational constraints fetch failed: {str(e)}"}

    report_data = {
        "origin": origin,
        "destination": destination,
        "distance_miles": distance_miles,
        "distance_km": distance_km,
        "weather": weather_data,
        "fuel_efficiency": fuel_efficiency,
        "safety_factors": safety_factors,
        "route_data": route_data,
        "operational_constraints": operational_constraints,
    }

    return JsonResponse(report_data)

AIRPORT_COORDS = {
    "BLR": (77.7100, 12.9500),   # (longitude, latitude)
    "HBX": (74.7667, 15.3617),
    "TRV": (76.9200, 8.4820),
    "MAA": (80.1667, 13.1667),
    "DEL": (77.1025, 28.5616),
}

def fetch_turbulence_sigmets():
    url = "https://aviationweather.gov/adds/dataserver_current/httpparam"
    params = {
        "datasource": "sigmet",
        "requestType": "retrieve",
        "format": "xml",
        "hazardType": "Turbulence",
        "hoursBeforeNow": "4"
    }

    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)

    zones = []

    for sigmet in root.iter("SIGMET"):
        coords_str = sigmet.findtext("areaCoords") or sigmet.findtext("geometry")
        if coords_str:
            points = []
            for line in coords_str.strip().split():
                try:
                    lat, lon = map(float, line.strip().split(","))
                    points.append((lon, lat))  # shapely uses (lon, lat)
                except:
                    continue
            if len(points) >= 3:
                polygon = Polygon(points)
                zones.append(polygon)
    return zones

def compute_cost(route_points, turbulence_zones):
    route_line = LineString(route_points)
    cost = 0
    hits = []

    for zone in turbulence_zones:
        if route_line.intersects(zone):
            cost += 100
            hits.append(zone)

    return cost, hits

def turbulence(request):
    origin = request.GET.get('origin', 'BLR').strip().upper()
    destination = request.GET.get('destination', 'TRV').strip().upper()

    origin_coords = AIRPORT_COORDS.get(origin)
    dest_coords = AIRPORT_COORDS.get(destination)

    if not (origin_coords and dest_coords):
        return render(request, 'turbulence.html', {
            'error': "Invalid IATA code entered.",
            'map_html': "",
            'route_cost': 0,
            'affected_zones': 0,
            'origin': origin,
            'destination': destination
        })

    # Extract lon/lat tuples
    route_points = [origin_coords, dest_coords]  # [(lon, lat), (lon, lat)]

    # Fetch turbulence zones
    from shapely.geometry import Polygon
    
    raw_zones = fetch_turbulence_sigmets()

    # Convert all zone coordinate lists into Polygon objects
    sigmet_zones = []
    for zone in raw_zones:
        if isinstance(zone, Polygon):
            sigmet_zones.append(zone)
        elif isinstance(zone, list):
            try:
                poly = Polygon(zone)
                if poly.is_valid:
                    sigmet_zones.append(poly)
            except:
                continue

    cost, affected = compute_cost(route_points, sigmet_zones)

    # Center map between points
    center_lat = (origin_coords[1] + dest_coords[1]) / 2
    center_lon = (origin_coords[0] + dest_coords[0]) / 2

    # Create Folium map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)

    # Add route polyline: switch to (lat, lon) for folium
    folium.PolyLine(
        [(lat, lon) for lon, lat in route_points],
        color="blue",
        weight=5,
        tooltip=f"{origin} → {destination}"
    ).add_to(m)

    # Draw turbulence zones
    for zone in sigmet_zones:
        folium.Polygon(
            locations=[(lat, lon) for lon, lat in zone.exterior.coords],
            color='red',
            fill=True,
            fill_opacity=0.4,
            tooltip="Turbulence Zone"
        ).add_to(m)


    # Add origin and destination markers
    folium.Marker(
        location=(origin_coords[1], origin_coords[0]),
        popup=f"Origin: {origin}",
        icon=folium.Icon(color="green", icon="info-sign")
    ).add_to(m)

    folium.Marker(
        location=(dest_coords[1], dest_coords[0]),
        popup=f"Destination: {destination}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    m.add_child(MeasureControl())
    map_html = m._repr_html_()

    return render(request, 'turbulence.html', {
        'map_html': map_html,
        'route_cost': cost,
        'affected_zones': len(affected),
        'origin': origin,
        'destination': destination
    })

def about(request):
    return render(request, 'about.html')