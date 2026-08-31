from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.landuse_polygon import LandusePolygon


@admin.register(LandusePolygon)
class LandusePolygonAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'landuse', 'osm_id')
    list_filter = ('landuse',)
    search_fields = ('name',)
