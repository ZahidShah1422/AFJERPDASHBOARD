from rest_framework import viewsets
from .models import Vehicle, MaintenanceTask, FuelConsumption
from .serializers import VehicleSerializer, MaintenanceTaskSerializer, FuelConsumptionSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class MaintenanceTaskViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceTask.objects.all()
    serializer_class = MaintenanceTaskSerializer

class FuelConsumptionViewSet(viewsets.ModelViewSet):
    queryset = FuelConsumption.objects.all()
    serializer_class = FuelConsumptionSerializer

