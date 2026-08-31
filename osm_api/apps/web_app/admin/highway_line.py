from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.highway_line import HighwayLine


@admin.register(HighwayLine)
class HighwayLineAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'highway', 'oneway', 'bridge', 'tunnel', 'osm_id')
    list_filter = ('highway', 'oneway', 'bridge', 'tunnel')
    search_fields = ('name', 'ref')
