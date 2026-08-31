from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.railway_line import RailwayLine


@admin.register(RailwayLine)
class RailwayLineAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'railway', 'bridge', 'tunnel', 'osm_id')
    list_filter = ('railway', 'bridge', 'tunnel')
    search_fields = ('name',)
