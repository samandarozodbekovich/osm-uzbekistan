from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.poi_polygon import PoiPolygon


@admin.register(PoiPolygon)
class PoiPolygonAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'name_en', 'amenity', 'leisure', 'tourism', 'osm_id')
    list_filter = ('amenity', 'leisure', 'tourism')
    search_fields = ('name', 'name_en', 'amenity')
