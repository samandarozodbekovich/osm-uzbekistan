from rest_framework import serializers

from ..models import OsmRelationTag


class OsmRelationTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmRelationTag
        fields = ('id', 'k', 'v')
