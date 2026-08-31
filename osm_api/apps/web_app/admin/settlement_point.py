from django.contrib import admin
from .map_mixin import GeoMapMixin
from ..models.settlement_point import SettlementPoint


@admin.register(SettlementPoint)
class SettlementPointAdmin(GeoMapMixin, admin.ModelAdmin):
    list_display = ('fid', 'name', 'name_en', 'place', 'population', 'osm_id')
    list_filter = ('place',)
    search_fields = ('name', 'name_en')
