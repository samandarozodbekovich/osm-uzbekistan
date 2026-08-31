from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.parking_polygon import ParkingPolygon


@admin.register(ParkingPolygon)
class ParkingPolygonAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'parking', 'access', 'capacity', 'osm_id')
    list_filter = ('parking', 'access')
    search_fields = ('name',)
