from django.contrib import admin
from .models import Route, Trip, RouteMetrics, School, RouteChange, Incident, RouteCompletion

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'start_point', 'end_point', 'schedule_date', 'created_at', 'updated_at')
    list_filter = ('status', 'schedule_date')
    search_fields = ('name', 'start_point', 'end_point')
    ordering = ('-created_at',)

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('route', 'start_time', 'end_time', 'status', 'driver', 'vehicle', 'created_at', 'updated_at')
    list_filter = ('status', 'start_time', 'end_time')
    search_fields = ('route__name', 'driver', 'vehicle')
    ordering = ('-start_time',)

@admin.register(RouteMetrics)
class RouteMetricsAdmin(admin.ModelAdmin):
    list_display = ('route', 'date', 'late_pickup_minutes', 'timely_pickup', 'late_dropoff_minutes', 'timely_dropoff')
    list_filter = ('date', 'timely_pickup', 'timely_dropoff')
    search_fields = ('route__name',)
    ordering = ('-date',)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'address', 'contact_number', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'contact_number')
    ordering = ('-created_at',)

@admin.register(RouteChange)
class RouteChangeAdmin(admin.ModelAdmin):
    list_display = ('route', 'change_type', 'change_date', 'reason', 'created_at')
    list_filter = ('change_type', 'change_date')
    search_fields = ('route__name', 'reason')
    ordering = ('-change_date',)

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('route', 'incident_type', 'incident_date', 'description', 'is_resolved', 'severity', 'created_at', 'updated_at')
    list_filter = ('incident_type', 'is_resolved', 'severity', 'incident_date')
    search_fields = ('route__name', 'description', 'root_cause')
    ordering = ('-incident_date',)

@admin.register(RouteCompletion)
class RouteCompletionAdmin(admin.ModelAdmin):
    list_display = ('route', 'date', 'is_completed', 'is_on_time')
    list_filter = ('date', 'is_completed', 'is_on_time')
    search_fields = ('route__name',)
    ordering = ('-date',)
