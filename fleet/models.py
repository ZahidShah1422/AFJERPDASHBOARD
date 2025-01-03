from django.db import models

class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[
        ('AVAILABLE', 'Available'),
        ('IN_USE', 'In Use'),
        ('MAINTENANCE', 'Under Maintenance')
    ])
    next_service_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.type})"

class MaintenanceTask(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.vehicle.name} - {self.task}"

class FuelConsumption(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.vehicle.name} - {self.date} - {self.amount}"

