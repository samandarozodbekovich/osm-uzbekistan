from django.contrib import admin
from ..models.osm_way_node import OsmWayNode


@admin.register(OsmWayNode)
class OsmWayNodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'way', 'node', 'sequence_id')
