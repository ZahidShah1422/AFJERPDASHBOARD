from django.contrib import admin
from .models import Employee, Leave, Attendance

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'position', 'email', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'email', 'department', 'position')
    ordering = ('name',)

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'start_date', 'end_date', 'leave_type', 'status')
    list_filter = ('leave_type', 'status', 'start_date', 'end_date')
    search_fields = ('employee__name', 'leave_type', 'status')
    ordering = ('start_date',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'date', 'is_present')
    list_filter = ('is_present', 'date')
    search_fields = ('employee__name', 'date')
    ordering = ('date',)
