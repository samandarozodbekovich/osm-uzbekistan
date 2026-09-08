from rest_framework import serializers

from ..models import OsmRelationMember


class OsmRelationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmRelationMember
        fields = ('sequence_id', 'member_type', 'member_id', 'role')
