from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hr/', views.hr_dashboard, name='hr_dashboard'),
    path('fleet/', views.fleet_dashboard, name='fleet_dashboard'),
    path('routes/', views.routes_dashboard, name='routes_dashboard'),
    path('finance/', views.finance_dashboard, name='finance_dashboard'),
    path('schedule-maintenance/', views.schedule_maintenance, name='schedule_maintenance'),
]

