from django.contrib import admin
from .models import Theatre, Performance, Review

@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ['title', 'theatre', 'date', 'time', 'status']
    list_filter = ['status', 'theatre', 'date']
    search_fields = ['title', 'theatre__name']
    date_hierarchy = 'date'
    ordering = ['-date', '-time']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['performance', 'author_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['performance__title', 'author_name']