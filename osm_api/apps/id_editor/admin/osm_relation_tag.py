from django.contrib import admin
from ..models.osm_relation_tag import OsmRelationTag


@admin.register(OsmRelationTag)
class OsmRelationTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'relation', 'k', 'v')
    search_fields = ('k', 'v')
