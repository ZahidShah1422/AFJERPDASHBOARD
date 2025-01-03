from rest_framework import viewsets
from .models import Route, Trip, Incident, RouteMetrics, School, RouteChange, RouteCompletion
from .serializers import RouteSerializer, TripSerializer, IncidentSerializer
from django.shortcuts import render
from django.db.models import Count, Avg, Q, F, Sum, DurationField
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer


def routes_dashboard(request):
    # Get date range from request or default to today
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_route = request.GET.get('route')
    selected_location = request.GET.get('location')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date()

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = start_date

    # Base queryset with date range filter
    base_metrics_query = RouteMetrics.objects.filter(date__range=[start_date, end_date])
    if selected_route:
        base_metrics_query = base_metrics_query.filter(route_id=selected_route)
    if selected_location:
        base_metrics_query = base_metrics_query.filter(
            Q(route__start_point=selected_location) | Q(route__end_point=selected_location)
        )

    # Routes Statistics
    routes_stats = {
        'total_routes': Route.objects.count(),
        'active_routes': Route.objects.filter(status='ACTIVE').count(),
        'on_hold_routes': Route.objects.filter(status='ON_HOLD').count(),
        'ended_routes': Route.objects.filter(status='ENDED').count(),
    }

    # Calculate metrics
    metrics = {
        'avg_late_pickup': base_metrics_query.aggregate(
            avg=Avg('late_pickup_minutes')
        )['avg'] or 0,
        
        'timely_dropoff_percentage': (
            base_metrics_query.filter(timely_dropoff=True).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
        
        'late_dropoff_school_percentage': (
            base_metrics_query.filter(late_school_dropoff_minutes__gt=0).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
        
        'late_drop_home_percentage': (
            base_metrics_query.filter(late_home_dropoff=True).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
        
        'timely_pickup_percentage': (
            base_metrics_query.filter(timely_pickup=True).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
        
        'timely_home_pickup_percentage': (
            base_metrics_query.filter(timely_home_pickup=True).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
        
        'timely_school_pickup_percentage': (
            base_metrics_query.filter(late_school_pickup_minutes=0).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
        
        'avg_late_school_dropoff': base_metrics_query.aggregate(
            avg=Avg('late_school_dropoff_minutes')
        )['avg'] or 0,
        
        'late_home_pickup_percentage': (
            base_metrics_query.filter(late_home_pickup=True).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
        
        'late_school_pickup_percentage': (
            base_metrics_query.filter(late_school_pickup_minutes__gt=0).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
        
        'avg_late_school_pickup': base_metrics_query.aggregate(
            avg=Avg('late_school_pickup_minutes')
        )['avg'] or 0,
        
        'timely_school_dropoff_percentage': (
            base_metrics_query.filter(late_school_dropoff_minutes=0).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
        
        'timely_home_dropoff_percentage': (
            base_metrics_query.filter(timely_home_dropoff=True).count() /
            base_metrics_query.count() * 100 if base_metrics_query.exists() else 0
        ),
    }

    # Incidents and Changes
    incidents_data = {
        'breakdown_count': Incident.objects.filter(
            incident_type='BREAKDOWN',
            incident_date__range=[start_date, end_date]
        ).count(),
        'accidents_count': Incident.objects.filter(
            incident_type='ACCIDENT',
            incident_date__range=[start_date, end_date]
        ).count(),
    }

    changes_data = {
        'vehicle_changes': RouteChange.objects.filter(
            change_type='VEHICLE',
            change_date__range=[start_date, end_date]
        ).count(),
        'staff_changes': RouteChange.objects.filter(
            change_type='STAFF',
            change_date__range=[start_date, end_date]
        ).count(),
    }

    # Schools Statistics
    schools_stats = {
        'total_schools': School.objects.count(),
        'active_schools': School.objects.filter(is_active=True).count(),
        'inactive_schools': School.objects.filter(is_active=False).count(),
    }

    # Route Performance
    route_performance = RouteCompletion.objects.filter(date__range=[start_date, end_date]).aggregate(
        scheduled=Count('id'),
        completed=Count('id', filter=Q(is_completed=True)),
        on_time=Count('id', filter=Q(is_on_time=True))
    )

    # Incident Types and Frequency
    incident_types = Incident.objects.filter(incident_date__range=[start_date, end_date]).values('incident_type').annotate(count=Count('id'))

    # Route Efficiency
    route_efficiency = Route.objects.filter(schedule_date__range=[start_date, end_date]).aggregate(
        avg_planned=Avg('planned_duration'),
        avg_actual=Avg('actual_duration')
    )

    # Incident Severity
    incident_severity = Incident.objects.filter(incident_date__range=[start_date, end_date]).values('severity').annotate(count=Count('id'))

    # Route List
    routes = Route.objects.filter(schedule_date__range=[start_date, end_date]).annotate(
        driver_name=F('trips__driver')
    ).values('id', 'name', 'driver_name', 'start_point', 'end_point', 'status')

    # Incidents Table
    incidents = Incident.objects.filter(incident_date__range=[start_date, end_date]).values(
        'id', 'incident_type', 'severity', 'is_resolved', 'incident_date', 'route__name'
    )

    context = {
        'routes_stats': routes_stats,
        'metrics': metrics,
        'incidents_data': incidents_data,
        'changes_data': changes_data,
        'schools_stats': schools_stats,
        'start_date': start_date,
        'end_date': end_date,
        'selected_route': selected_route,
        'selected_location': selected_location,
        # Add routes list for dropdown
        'routes_list': Route.objects.values('id', 'name'),
        # Add locations list for dropdown
        'locations_list': Route.objects.values_list('start_point', 'end_point').distinct(),
        'route_performance': route_performance,
        'incident_types': list(incident_types),
        'route_efficiency': route_efficiency,
        'incident_severity': list(incident_severity),
        'routes': list(routes),
        'incidents': list(incidents),
    }

    return render(request, 'frontend/routes_dashboard.html', context)

