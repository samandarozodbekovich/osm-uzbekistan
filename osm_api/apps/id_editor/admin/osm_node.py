from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin
from ..models.osm_node import OsmNode


@admin.register(OsmNode)
class OsmNodeAdmin(LeafletGeoAdmin):
    list_display = ('id', 'version', 'visible', 'lat', 'lon', 'timestamp', 'changeset')
    list_filter = ('visible',)
    search_fields = ('id',)
