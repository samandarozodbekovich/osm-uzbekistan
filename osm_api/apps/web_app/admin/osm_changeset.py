from django.contrib import admin
from ..models.osm_changeset import OsmChangeset


@admin.register(OsmChangeset)
class OsmChangesetAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'uid', 'created_at', 'closed_at', 'open')
    list_filter = ('open',)
    search_fields = ('user',)
