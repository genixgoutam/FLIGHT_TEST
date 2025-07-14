from django.contrib import admin
from .models import Airport, Flight, Route, RouteStop, WeatherCondition, FuelEfficiency, SafetyFactor, OperationalConstraint, Waypoint

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'latitude', 'longitude', 'timezone')
    search_fields = ('code', 'name')
    list_filter = ('timezone',)

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'origin', 'destination', 'departure_time', 'arrival_time', 'aircraft_type', 'airline', 'total_cost', 'optimization_complexity')
    list_filter = ('aircraft_type', 'airline', 'optimization_complexity')
    search_fields = ('flight_number', 'origin__code', 'destination__code', 'airline')
    filter_horizontal = ('weather_conditions', 'safety_factors', 'operational_constraints', 'flight_waypoints')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin', 'destination', 'total_distance', 'total_cost', 'optimization_complexity', 'complexity_score')
    list_filter = ('optimization_complexity',)
    search_fields = ('name', 'origin__code', 'destination__code')
    filter_horizontal = ('weather_conditions', 'safety_factors', 'operational_constraints', 'route_waypoints')

@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('route', 'airport', 'stop_order', 'layover_duration')
    list_filter = ('stop_order',)
    search_fields = ('route__name', 'airport__code')

@admin.register(WeatherCondition)
class WeatherConditionAdmin(admin.ModelAdmin):
    list_display = ('weather_type', 'severity', 'temperature', 'wind_speed', 'location_lat', 'location_lon', 'timestamp')
    list_filter = ('weather_type', 'severity', 'timestamp')
    search_fields = ('weather_type', 'severity')

@admin.register(FuelEfficiency)
class FuelEfficiencyAdmin(admin.ModelAdmin):
    list_display = ('aircraft_type', 'altitude', 'speed', 'fuel_per_mile', 'efficiency_rating', 'timestamp')
    list_filter = ('aircraft_type', 'efficiency_rating', 'timestamp')
    search_fields = ('aircraft_type',)

@admin.register(SafetyFactor)
class SafetyFactorAdmin(admin.ModelAdmin):
    list_display = ('category', 'risk_level', 'active', 'timestamp')
    list_filter = ('category', 'risk_level', 'active', 'timestamp')
    search_fields = ('category', 'description')

@admin.register(OperationalConstraint)
class OperationalConstraintAdmin(admin.ModelAdmin):
    list_display = ('constraint_type', 'name', 'impact_score', 'active', 'start_time', 'end_time')
    list_filter = ('constraint_type', 'active', 'start_time', 'end_time')
    search_fields = ('name', 'description')

@admin.register(Waypoint)
class WaypointAdmin(admin.ModelAdmin):
    list_display = ('sequence_number', 'waypoint_type', 'latitude', 'longitude', 'altitude', 'route')
    list_filter = ('waypoint_type', 'route')
    search_fields = ('waypoint_type', 'route__name')

class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1 