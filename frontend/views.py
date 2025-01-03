import random
from django.shortcuts import render
from django.db.models import Count, Sum, F, Avg, Q, Case, When, Value, CharField, ExpressionWrapper, DurationField, IntegerField
from django.db.models.functions import TruncMonth, Cast
from django.utils import timezone
from datetime import datetime, timedelta
from hr.models import Employee, Leave
from fleet.models import Vehicle, MaintenanceTask, FuelConsumption
from routes.models import Route, Trip, Incident, RouteMetrics, School, RouteChange, RouteCompletion
from finance.models import Revenue, Expense, Invoice

def index(request):
    time_filter = request.GET.get('filter', 'today')
    today = timezone.now().date()

    if time_filter == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Default to 'today' if custom dates are not provided
            start_date = end_date = today
    elif time_filter == 'this_week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif time_filter == 'this_month':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:  # today
        start_date = end_date = today

    # Calculate the previous period for comparisons
    period_length = (end_date - start_date).days + 1
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period_length - 1)

    # HR Overview Data
    employees_on_leave = Leave.objects.filter(
        start_date__lte=end_date,
        end_date__gte=start_date,
        status='APPROVED'
    ).count()

    total_employees = Employee.objects.filter(is_active=True).count()
    
    pending_leaves = Leave.objects.filter(status='PENDING').count()

    # Calculate employee growth rate
    new_employees = Employee.objects.filter(
        hire_date__range=(start_date, end_date),
        is_active=True
    ).count()
    previous_employees = Employee.objects.filter(
        hire_date__range=(previous_start, previous_end),
        is_active=True
    ).count()
    employee_growth = ((new_employees - previous_employees) / previous_employees * 100) if previous_employees > 0 else 0

    # Fleet Status Data
    total_vehicles = Vehicle.objects.count()
    vehicles_maintenance = Vehicle.objects.filter(status='MAINTENANCE').count()
    
    # Calculate fuel cost trend
    current_fuel = FuelConsumption.objects.filter(
        date__range=(start_date, end_date)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    previous_fuel = FuelConsumption.objects.filter(
        date__range=(previous_start, previous_end)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    fuel_cost_change = ((current_fuel - previous_fuel) / previous_fuel * 100) if previous_fuel > 0 else 0

    # Routes Overview Data
    routes_today = Route.objects.filter(
        schedule_date__range=(start_date, end_date)
    ).count()
    
    completed_trips = Trip.objects.filter(
        status='COMPLETED',
        end_time__date__range=(start_date, end_date)
    )
    total_trips = Trip.objects.filter(start_time__date__range=(start_date, end_date))
    on_time_rate = (completed_trips.count() / total_trips.count() * 100) if total_trips.count() > 0 else 0
    
    previous_completed_trips = Trip.objects.filter(
        status='COMPLETED',
        end_time__date__range=(previous_start, previous_end)
    )
    previous_total_trips = Trip.objects.filter(start_time__date__range=(previous_start, previous_end))
    previous_on_time_rate = (previous_completed_trips.count() / previous_total_trips.count() * 100) if previous_total_trips.count() > 0 else 0
    
    on_time_change = on_time_rate - previous_on_time_rate
    
    open_incidents = Trip.objects.filter(
        status='INCIDENT',
        start_time__date__range=(start_date, end_date)
    ).count()

    # Financial Summary Data
    current_revenue = Revenue.objects.filter(
        date__range=(start_date, end_date)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    previous_revenue = Revenue.objects.filter(
        date__range=(previous_start, previous_end)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
    
    pending_payments = Invoice.objects.filter(
        status='PENDING',
        due_date__range=(start_date, end_date)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    current_expenses = Expense.objects.filter(
        date__range=(start_date, end_date)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    previous_expenses = Expense.objects.filter(
        date__range=(previous_start, previous_end)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    expenses_change = ((current_expenses - previous_expenses) / previous_expenses * 100) if previous_expenses > 0 else 0

    context = {
        'time_filter': time_filter,
        'start_date': start_date,
        'end_date': end_date,
        'hr_data': {
            'employees_on_leave': employees_on_leave,
            'total_employees': total_employees,
            'employee_growth': employee_growth,
            'pending_leaves': pending_leaves,
        },
        'fleet_data': {
            'total_vehicles': total_vehicles,
            'vehicles_maintenance': vehicles_maintenance,
            'fuel_costs': current_fuel,
            'fuel_cost_change': fuel_cost_change,
        },
        'routes_data': {
            'routes_today': routes_today,
            'on_time_rate': on_time_rate,
            'on_time_change': on_time_change,
            'open_incidents': open_incidents,
        },
        'finance_data': {
            'revenue': current_revenue,
            'revenue_change': revenue_change,
            'pending_payments': pending_payments,
            'expenses': current_expenses,
            'expenses_change': expenses_change,
        }
    }
    
    return render(request, 'frontend/index.html', context)

def hr_dashboard(request):
    # Fetch HR-specific data here
    employees = Employee.objects.filter(is_active=True)
    leaves = Leave.objects.filter(status='APPROVED')
    
    context = {
        'employees': employees,
        'leaves': leaves,
    }
    return render(request, 'frontend/hr_dashboard.html', context)

def fleet_dashboard(request):
    # Fetch fleet-specific data here
    vehicles = Vehicle.objects.all()
    maintenance_tasks = MaintenanceTask.objects.all()
    
    context = {
        'vehicles': vehicles,
        'maintenance_tasks': maintenance_tasks,
    }
    return render(request, 'frontend/fleet_dashboard.html', context)

def routes_dashboard(request):
    # Get date range from request or default to last 30 days
    end_date = request.GET.get('end_date')
    start_date = request.GET.get('start_date')
    selected_route = request.GET.get('route')
    selected_location = request.GET.get('location')

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)

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
        'routes_list': Route.objects.values('id', 'name'),
        'locations_list': Route.objects.values_list('start_point', 'end_point').distinct(),
        'route_performance': route_performance,
        'incident_types': list(incident_types),
        'route_efficiency': route_efficiency,
        'incident_severity': list(incident_severity),
        'routes': list(routes),
        'incidents': list(incidents),
    }

    return render(request, 'frontend/routes_dashboard.html', context)
def finance_dashboard(request):
    # Generate dummy data for the last 12 months
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)

    # Dummy financial data
    financial_data = []
    for i in range(12):
        month = end_date - timedelta(days=30 * i)
        financial_data.append({
            'month': month.strftime('%B %Y'),
            'revenue': random.randint(50000, 100000),
            'expenses': random.randint(30000, 80000)
        })
    financial_data.reverse()

    # Dummy expense breakdown
    expense_categories = ['Salaries', 'Rent', 'Utilities', 'Marketing', 'Equipment', 'Miscellaneous']
    expense_breakdown = [
        {'category': category, 'total': random.randint(10000, 50000)}
        for category in expense_categories
    ]

    # Dummy invoice status
    invoice_status = [
        {'status': 'Paid', 'count': random.randint(50, 100), 'total': random.randint(100000, 200000)},
        {'status': 'Pending', 'count': random.randint(20, 50), 'total': random.randint(50000, 100000)},
        {'status': 'Overdue', 'count': random.randint(5, 20), 'total': random.randint(10000, 50000)}
    ]

    # Dummy overdue payments
    overdue_payments = [
        {
            'id': f'INV-{random.randint(1000, 9999)}',
            'client': f'Client {i}',
            'amount': random.randint(1000, 10000),
            'due_date': end_date - timedelta(days=random.randint(1, 60))
        }
        for i in range(5)
    ]

    # Dummy invoices
    invoices = [
        {
            'id': f'INV-{random.randint(1000, 9999)}',
            'client': f'Client {i}',
            'amount': random.randint(1000, 10000),
            'date': end_date - timedelta(days=random.randint(1, 365)),
            'status': random.choice(['Paid', 'Pending', 'Overdue'])
        }
        for i in range(20)
    ]

    # Dummy expenditures
    expenditures = [
        {
            'date': end_date - timedelta(days=random.randint(1, 365)),
            'category': random.choice(expense_categories),
            'department': random.choice(['Sales', 'Marketing', 'Operations', 'IT']),
            'amount': random.randint(100, 5000)
        }
        for _ in range(20)
    ]

    # Dummy revenue growth
    revenue_growth = [
        {
            'month': (end_date - timedelta(days=30 * i)).strftime('%B %Y'),
            'total': random.randint(50000, 100000)
        }
        for i in range(12)
    ]
    revenue_growth.reverse()

    # Dummy departmental expenses
    departments = ['Sales', 'Marketing', 'Operations', 'IT']
    dept_expenses = [
        {
            'department': dept,
            'category': cat,
            'total': random.randint(5000, 20000)
        }
        for dept in departments
        for cat in expense_categories
    ]

    # Dummy invoice aging
    invoice_aging = [
        {'age_category': '0-30 days', 'count': random.randint(20, 50), 'total': random.randint(50000, 100000)},
        {'age_category': '31-60 days', 'count': random.randint(10, 30), 'total': random.randint(20000, 50000)},
        {'age_category': '61-90 days', 'count': random.randint(5, 15), 'total': random.randint(10000, 30000)},
        {'age_category': '90+ days', 'count': random.randint(1, 10), 'total': random.randint(5000, 20000)}
    ]

    # Dummy budget summary data
    budget_categories = ['Salaries', 'Rent', 'Utilities', 'Marketing', 'Equipment', 'Miscellaneous']
    budget_summary = [
        {
            'category': category,
            'budgeted': random.randint(10000, 50000),
            'actual': random.randint(8000, 55000),
        } for category in budget_categories
    ]
    for item in budget_summary:
        item['variance'] = item['budgeted'] - item['actual']

    context = {
        'financial_data': financial_data,
        'expense_breakdown': expense_breakdown,
        'invoice_status': invoice_status,
        'overdue_payments': overdue_payments,
        'invoices': invoices,
        'expenditures': expenditures,
        'revenue_growth': revenue_growth,
        'dept_expenses': dept_expenses,
        'invoice_aging': invoice_aging,
        'budget_summary': budget_summary,
    }

    return render(request, 'frontend/finance_dashboard.html', context)

def schedule_maintenance(request):
    return render(request, 'frontend/schedule-maintenance.html')

