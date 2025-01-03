from django.contrib import admin
from .models import Vehicle, MaintenanceTask, FuelConsumption

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'status', 'next_service_date')
    list_filter = ('type', 'status', 'next_service_date')
    search_fields = ('name', 'type', 'status')
    ordering = ('-next_service_date',)

@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'task', 'due_date')
    list_filter = ('due_date', 'vehicle__name')
    search_fields = ('task', 'vehicle__name')
    ordering = ('-due_date',)

@admin.register(FuelConsumption)
class FuelConsumptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'date', 'amount')
    list_filter = ('date', 'vehicle__name')
    search_fields = ('vehicle__name',)
    ordering = ('-date',)
