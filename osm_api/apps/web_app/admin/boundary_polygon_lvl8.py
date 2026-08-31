from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.boundary_polygon_lvl8 import BoundaryPolygonLvl8


@admin.register(BoundaryPolygonLvl8)
class BoundaryPolygonLvl8Admin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'name_en', 'admin_lvl', 'osm_id')
    search_fields = ('name', 'name_en')
