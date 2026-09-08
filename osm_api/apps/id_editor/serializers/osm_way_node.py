from rest_framework import serializers

from ..models import OsmWayNode


class OsmWayNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmWayNode
        fields = ('sequence_id', 'node')
