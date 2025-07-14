from rest_framework import serializers
from .models import Airport, Flight, WeatherCondition, FuelEfficiency, SafetyFactor, OperationalConstraint

# Serializer for Airport model
class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'

# Serializer for Flight model
class FlightSerializer(serializers.ModelSerializer):
    origin = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    class Meta:
        model = Flight
        fields = '__all__'

# Serializer for WeatherCondition model
class WeatherConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherCondition
        fields = '__all__'

# Serializer for FuelEfficiency model
class FuelEfficiencySerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelEfficiency
        fields = '__all__'

# Serializer for SafetyFactor model
class SafetyFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyFactor
        fields = '__all__'

# Serializer for OperationalConstraint model
class OperationalConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalConstraint
        fields = '__all__'

# Modular: Add more serializers as needed for new models or API endpoints 