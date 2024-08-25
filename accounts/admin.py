# accounts/admin.py
from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'last_online') 
    search_fields = ('user__username', 'name')
    list_filter = ('last_online',) 

    raw_id_fields = ('user',)
