from django.contrib import admin
from .models import Card

class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'short_name', 'suit']
    search_fields = ['suit']

admin.site.register(Card, CardAdmin)
