from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.boundary_polygon_lvl4 import BoundaryPolygonLvl4


@admin.register(BoundaryPolygonLvl4)
class BoundaryPolygonLvl4Admin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'name_en', 'admin_lvl', 'osm_id')
    search_fields = ('name', 'name_en')
