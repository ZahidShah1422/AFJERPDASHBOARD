from django.db import models
from django.utils import timezone
from django.db.models import DurationField

class Route(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ON_HOLD', 'On Hold'),
        ('ENDED', 'Ended')
    ]
    
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    schedule_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    planned_duration = models.DurationField(help_text="Planned duration of the route", null=True, blank=True)
    actual_duration = models.DurationField(help_text="Actual duration of the route", null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

class Trip(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    driver = models.CharField(max_length=100)
    vehicle = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trip for {self.route.name} on {self.start_time.date()}"

class RouteMetrics(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField()
    
    late_pickup_minutes = models.IntegerField(default=0)
    timely_pickup = models.BooleanField(default=True)
    late_school_pickup_minutes = models.IntegerField(default=0)
    
    late_dropoff_minutes = models.IntegerField(default=0)
    timely_dropoff = models.BooleanField(default=True)
    late_school_dropoff_minutes = models.IntegerField(default=0)
    
    late_home_pickup = models.BooleanField(default=False)
    late_home_dropoff = models.BooleanField(default=False)
    timely_home_pickup = models.BooleanField(default=True)
    timely_home_dropoff = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['route', 'date'])
        ]

    def __str__(self):
        return f"Metrics for {self.route.name} on {self.date}"

class School(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class RouteChange(models.Model):
    CHANGE_TYPE_CHOICES = [
        ('VEHICLE', 'Vehicle Change'),
        ('STAFF', 'Staff Change')
    ]
    
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='changes')
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    change_date = models.DateField()
    reason = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.change_type} for {self.route.name} on {self.change_date}"

class Incident(models.Model):
    INCIDENT_TYPE_CHOICES = [
        ('ACCIDENT', 'Accident'),
        ('BREAKDOWN', 'Breakdown'),
        ('OTHER', 'Other')
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='incidents', null=True, blank=True)
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPE_CHOICES, default='OTHER')
    incident_date = models.DateField(default=timezone.now)
    description = models.TextField()
    resolution_time = models.IntegerField(help_text="Resolution time in minutes", null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='LOW')
    root_cause = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.incident_type} on {self.incident_date} for {self.route.name if self.route else 'Unknown Route'}"


class RouteCompletion(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField()
    is_completed = models.BooleanField(default=False)
    is_on_time = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.route.name} completion on {self.date}"

