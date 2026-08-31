from django.contrib import admin
from ..models.osm_relation_member import OsmRelationMember


@admin.register(OsmRelationMember)
class OsmRelationMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'relation', 'member_type', 'member_id', 'role', 'sequence_id')
    list_filter = ('member_type',)
