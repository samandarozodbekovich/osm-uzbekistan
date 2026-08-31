from django.contrib import admin
from ..models.osm_relation import OsmRelation


@admin.register(OsmRelation)
class OsmRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'visible', 'timestamp', 'changeset')
    list_filter = ('visible',)
