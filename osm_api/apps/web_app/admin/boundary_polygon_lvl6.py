from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.boundary_polygon_lvl6 import BoundaryPolygonLvl6


@admin.register(BoundaryPolygonLvl6)
class BoundaryPolygonLvl6Admin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'name_en', 'admin_lvl', 'osm_id')
    search_fields = ('name', 'name_en')
