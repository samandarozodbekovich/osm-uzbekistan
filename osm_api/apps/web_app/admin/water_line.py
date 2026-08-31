from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.water_line import WaterLine


@admin.register(WaterLine)
class WaterLineAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'waterway', 'osm_id')
    list_filter = ('waterway',)
    search_fields = ('name',)
