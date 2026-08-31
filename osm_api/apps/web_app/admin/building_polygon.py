from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.building_polygon import BuildingPolygon


@admin.register(BuildingPolygon)
class BuildingPolygonAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'building', 'a_strt', 'a_hsnmbr', 'osm_id')
    list_filter = ('building',)
    search_fields = ('name', 'a_strt', 'a_hsnmbr')
