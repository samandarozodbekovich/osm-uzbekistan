from django.contrib import admin
from ..models.osm_meta import OsmMeta


@admin.register(OsmMeta)
class OsmMetaAdmin(admin.ModelAdmin):
    list_display = ('osm_id', 'osm_type', 'version', 'user', 'timestamp', 'changeset')
    list_filter = ('osm_type',)
    search_fields = ('user',)
