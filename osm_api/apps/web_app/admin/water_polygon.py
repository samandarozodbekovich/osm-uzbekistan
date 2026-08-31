from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.water_polygon import WaterPolygon


@admin.register(WaterPolygon)
class WaterPolygonAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'osm_id')
    search_fields = ('name',)
