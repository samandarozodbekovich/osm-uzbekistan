from rest_framework import serializers

from ..models import OsmRelation
from .osm_relation_tag import OsmRelationTagSerializer
from .osm_relation_member import OsmRelationMemberSerializer


class OsmRelationSerializer(serializers.ModelSerializer):
    tags = OsmRelationTagSerializer(source='tags_set', many=True, read_only=True)
    members = OsmRelationMemberSerializer(many=True, read_only=True)

    class Meta:
        model = OsmRelation
        fields = ('id', 'version', 'visible', 'timestamp', 'changeset', 'tags', 'members')
