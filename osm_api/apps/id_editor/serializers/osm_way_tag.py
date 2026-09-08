from rest_framework import serializers

from ..models import OsmWayTag


class OsmWayTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmWayTag
        fields = ('id', 'k', 'v')
