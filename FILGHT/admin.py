from django.contrib import admin
from .models import Airport, Flight, Route, RouteStop

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'latitude', 'longitude', 'timezone')
    search_fields = ('code', 'name')
    list_filter = ('timezone',)

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'origin', 'destination', 'departure_time', 'arrival_time', 'aircraft_type', 'airline', 'total_cost')
    search_fields = ('flight_number', 'origin__code', 'destination__code', 'airline')
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin', 'destination', 'total_distance', 'total_cost', 'complexity_score')
    search_fields = ('name', 'origin__code', 'destination__code')

@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('route', 'airport', 'stop_order', 'layover_duration')
    list_filter = ('stop_order',)
    search_fields = ('route__name', 'airport__code')

class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1 