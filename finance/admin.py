from django.contrib import admin
from .models import Revenue, Expense, Invoice

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'description', 'source')
    list_filter = ('date', 'source')
    search_fields = ('description', 'source')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'description', 'category')
    list_filter = ('date', 'category')
    search_fields = ('description', 'category')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('client', 'amount', 'date', 'due_date', 'status')
    list_filter = ('status', 'date', 'due_date')
    search_fields = ('client', 'status')

