from django.contrib import admin
from .models import ContactMessage
# Register your models here.







@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # Columns to show in list view
    list_display = ['name', 'email', 'subject', 'date_sent', 'is_read']
    
    # Add filters on the right side
    list_filter = ['is_read', 'date_sent']
    
    # Search bar
    search_fields = ['name', 'email', 'subject', 'message']
    
    # Make date_sent read-only
    readonly_fields = ['date_sent']
    
    # Make message field bigger
    fields = ['name', 'email', 'subject', 'message', 'date_sent', 'is_read']
    
    # Default ordering (newest first)
    ordering = ['-date_sent']
    
    # Add "Mark as Read" action
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as Read"

