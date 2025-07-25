from django.db import models
import math
from datetime import time, timedelta

class Airport(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timezone = models.CharField(max_length=50, default='UTC')
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def distance_to(self, other_airport):
        """Calculate distance between two airports using Haversine formula"""
        R = 3959  # Earth's radius in miles
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other_airport.latitude), math.radians(other_airport.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
class AircraftProfile(models.Model):
    hex_code = models.CharField(max_length=10, unique=True)
    type = models.CharField(max_length=100)
    operator = models.CharField(max_length=100)
    registration = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.registration} ({self.hex_code})"
class OperationalConstraint(models.Model):
    aircraft = models.ForeignKey(AircraftProfile, on_delete=models.CASCADE, null=True, blank=True)
    constraint_type = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=20, default='N/A')
    notes = models.TextField()
    
    def __str__(self):
        return f"{self.constraint_type} for {self.aircraft.registration}"

class Flight(models.Model):
    """Flight model representing flights between airports"""
    flight_number = models.CharField(max_length=10, unique=True)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    duration = models.DurationField()
    distance = models.DecimalField(max_digits=8, decimal_places=2)
    fuel_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    aircraft_type = models.CharField(max_length=50, default='Boeing 737')
    airline = models.CharField(max_length=100, default='Generic Airlines')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
        
    def __str__(self):
        return f"{self.flight_number}: {self.origin.code} → {self.destination.code}"
    
    def calculate_fuel_cost(self, fuel_price_per_gallon=3.50):
        """Calculate fuel cost based on distance and aircraft efficiency"""
        # Different aircraft have different fuel efficiency
        efficiency_map = {
            'Boeing 737': 0.2,  # gallons per mile
            'Airbus A320': 0.18,
            'Boeing 777': 0.25,
            'Airbus A380': 0.3,
        }
        fuel_consumption_per_mile = efficiency_map.get(self.aircraft_type, 0.2)
        fuel_consumption = self.distance * fuel_consumption_per_mile
        self.fuel_cost = fuel_consumption * fuel_price_per_gallon
        return self.fuel_cost
    
    def calculate_duration(self):
        """Calculate flight duration based on distance and average speed"""
        # Different aircraft have different speeds
        speed_map = {
            'Boeing 737': 550,  # mph
            'Airbus A320': 540,
            'Boeing 777': 560,
            'Airbus A380': 570,
        }
        avg_speed = speed_map.get(self.aircraft_type, 550)
        self.duration = self.distance / avg_speed
        return self.duration
    
    def calculate_arrival_time(self):
        """Calculate arrival time based on departure time and duration"""
        departure_minutes = self.departure_time.hour * 60 + self.departure_time.minute
        duration_minutes = int(self.duration.total_seconds() / 60)
        arrival_minutes = departure_minutes + duration_minutes
        
        # Handle day overflow
        arrival_minutes = arrival_minutes % (24 * 60)
        
        hours = arrival_minutes // 60
        minutes = arrival_minutes % 60
        
        self.arrival_time = time(hours, minutes)
        return self.arrival_time
    
    def get_cost_breakdown(self):
        """Get detailed cost breakdown"""
        fuel_cost = self.calculate_fuel_cost()
        base_cost = self.total_cost - fuel_cost  # Other costs (crew, maintenance, etc.)
        
        return {
            'total_cost': self.total_cost,
            'fuel_cost': fuel_cost,
            'base_cost': base_cost,
            'fuel_percentage': (fuel_cost / self.total_cost * 100) if self.total_cost > 0 else 0
        }
    
    def get_weather_impact_score(self):
        """Calculate total weather impact score"""
        total_impact = 0
        weather_count = self.weather_conditions.count()
        
        if weather_count > 0:
            for weather in self.weather_conditions.all():
                total_impact += weather.get_impact_score()
            return total_impact / weather_count
        return 0
    
    def get_safety_risk_score(self):
        """Calculate total safety risk score"""
        total_risk = 0
        safety_count = self.safety_factors.count()
        
        if safety_count > 0:
            for safety in self.safety_factors.all():
                total_risk += safety.get_risk_score()
            return total_risk / safety_count
        return 0
    
    def get_operational_constraint_score(self):
        """Calculate total operational constraint impact"""
        total_impact = 0
        constraint_count = self.operational_constraints.count()
        
        if constraint_count > 0:
            for constraint in self.operational_constraints.all():
                if constraint.is_active_now():
                    total_impact += constraint.impact_score
            return total_impact / constraint_count
        return 0
    
    def get_complexity_score(self):
        """Calculate overall complexity score for high-dimensional optimization"""
        complexity_scores = {
            'low': 25, 'medium': 50, 'high': 75, 'extreme': 100
        }
        base_score = complexity_scores.get(self.optimization_complexity, 50)
        
        # Add penalties for various factors
        congestion_penalty = min(10, self.congestion_zones * 0.2)
        altitude_penalty = min(10, self.altitude_penalties * 0.1)
        delay_penalty = min(10, self.delay_penalties * 0.1)
        
        total_score = base_score + congestion_penalty + altitude_penalty + delay_penalty
        return min(100, total_score)

    class Meta:
        ordering = ['departure_time']

class Route(models.Model):
    """Model to store optimized routes"""
    name = models.CharField(max_length=100)
    origin = models.ForeignKey(Airport, related_name='route_origins', on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, related_name='route_destinations', on_delete=models.CASCADE)
    total_distance = models.FloatField()
    total_duration = models.FloatField()
    total_cost = models.FloatField()
    total_fuel_cost = models.FloatField()
    stops = models.ManyToManyField(Airport, through='RouteStop')
    created_at = models.DateTimeField(auto_now_add=True)
    
    congestion_zones = models.IntegerField(default=0)
    altitude_penalties = models.IntegerField(default=0)
    delay_penalties = models.IntegerField(default=0)
    
    # Additional metrics
    average_weather_impact = models.FloatField(default=0.0)
    average_safety_risk = models.FloatField(default=0.0)
    average_operational_constraint = models.FloatField(default=0.0)
    fuel_efficiency_rating = models.FloatField(default=0.0)
    complexity_score = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.name}: {self.origin.code} → {self.destination.code}"
    
    def get_cost_breakdown(self):
        """Get cost breakdown for the entire route"""
        return {
            'total_cost': self.total_cost,
            'fuel_cost': self.total_fuel_cost,
            'base_cost': self.total_cost - self.total_fuel_cost,
            'fuel_percentage': (self.total_fuel_cost / self.total_cost * 100) if self.total_cost > 0 else 0
        }
    
    # def get_weather_impact_score(self):
    #     """Calculate total weather impact score for the route"""
    #     total_impact = 0
    #     weather_count = self.weather_conditions.count()
        
    #     if weather_count > 0:
    #         for weather in self.weather_conditions.all():
    #             total_impact += weather.get_impact_score()
    #         return total_impact / weather_count
    #     return 0
    
    # def get_safety_risk_score(self):
    #     """Calculate total safety risk score for the route"""
    #     total_risk = 0
    #     safety_count = self.safety_factors.count()
        
    #     if safety_count > 0:
    #         for safety in self.safety_factors.all():
    #             total_risk += safety.get_risk_score()
    #         return total_risk / safety_count
    #     return 0
    
    # def get_operational_constraint_score(self):
    #     """Calculate total operational constraint impact for the route"""
    #     total_impact = 0
    #     constraint_count = self.operational_constraints.count()
        
    #     if constraint_count > 0:
    #         for constraint in self.operational_constraints.all():
    #             if constraint.is_active_now():
    #                 total_impact += constraint.impact_score
    #         return total_impact / constraint_count
    #     return 0
    
    def get_complexity_score(self):
        """Calculate overall complexity score for high-dimensional optimization"""
        complexity_scores = {
            'low': 25, 'medium': 50, 'high': 75, 'extreme': 100
        }
        base_score = complexity_scores.get(self.optimization_complexity, 50)
        
        congestion_penalty = min(10, self.congestion_zones * 0.2)
        altitude_penalty = min(10, self.altitude_penalties * 0.1)
        delay_penalty = min(10, self.delay_penalties * 0.1)
        
        total_score = base_score  + congestion_penalty + altitude_penalty + delay_penalty
        return min(100, total_score)
    
    def get_optimization_summary(self):
        """Get comprehensive optimization summary"""
        return {
            'complexity': {
                'level': self.optimization_complexity,
                'score': self.get_complexity_score(),
                'congestion_zones': self.congestion_zones,
                'penalties': {
                    'altitude': self.altitude_penalties,
                    'delay': self.delay_penalties
                }
            },
        }

class RouteStop(models.Model):
    """Intermediate stops in a route"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    stop_order = models.IntegerField()
    layover_duration = models.FloatField(default=1.5)  # in hours
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['stop_order']