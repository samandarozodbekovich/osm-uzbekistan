from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.boundary_polygon_lvl2 import BoundaryPolygonLvl2


@admin.register(BoundaryPolygonLvl2)
class BoundaryPolygonLvl2Admin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'name_en', 'admin_lvl', 'osm_id')
    search_fields = ('name', 'name_en')
