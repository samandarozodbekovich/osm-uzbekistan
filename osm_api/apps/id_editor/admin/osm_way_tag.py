from django.contrib import admin
from ..models.osm_way_tag import OsmWayTag


@admin.register(OsmWayTag)
class OsmWayTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'way', 'k', 'v')
    search_fields = ('k', 'v')
