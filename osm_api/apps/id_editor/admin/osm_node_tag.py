from django.contrib import admin
from ..models.osm_node_tag import OsmNodeTag


@admin.register(OsmNodeTag)
class OsmNodeTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'node', 'k', 'v')
    search_fields = ('k', 'v')
