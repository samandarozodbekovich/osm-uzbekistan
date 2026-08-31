from django.contrib import admin
from ..models.osm_way import OsmWay


@admin.register(OsmWay)
class OsmWayAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'visible', 'timestamp', 'changeset')
    list_filter = ('visible',)
