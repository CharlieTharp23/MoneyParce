from django.contrib import admin
from .models import Budget

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'month', 'year')
    list_filter = ('user', 'category', 'year', 'month')
    search_fields = ('category',)