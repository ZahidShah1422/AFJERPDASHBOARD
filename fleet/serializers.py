from rest_framework import serializers
from .models import Vehicle, MaintenanceTask, FuelConsumption

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class MaintenanceTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTask
        fields = '__all__'

class FuelConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelConsumption
        fields = '__all__'

