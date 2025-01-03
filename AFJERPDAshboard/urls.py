from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hr.views import EmployeeViewSet, LeaveViewSet, AttendanceViewSet
from fleet.views import VehicleViewSet, MaintenanceTaskViewSet, FuelConsumptionViewSet
from routes.views import RouteViewSet, TripViewSet, IncidentViewSet
from finance.views import RevenueViewSet, ExpenseViewSet, InvoiceViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'leaves', LeaveViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'maintenance-tasks', MaintenanceTaskViewSet)
router.register(r'fuel-consumptions', FuelConsumptionViewSet)
router.register(r'routes', RouteViewSet)
router.register(r'trips', TripViewSet)
router.register(r'incidents', IncidentViewSet)
router.register(r'revenues', RevenueViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('frontend.urls')),
]

