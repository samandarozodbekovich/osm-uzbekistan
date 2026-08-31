from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.vegetation_polygon import VegetationPolygon


@admin.register(VegetationPolygon)
class VegetationPolygonAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'osm_id')
    search_fields = ('name',)
