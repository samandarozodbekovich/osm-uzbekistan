from rest_framework import serializers

from ..models import OsmWay
from .osm_way_tag import OsmWayTagSerializer
from .osm_way_node import OsmWayNodeSerializer


class OsmWaySerializer(serializers.ModelSerializer):
    tags = OsmWayTagSerializer(source='tags_set', many=True, read_only=True)
    nodes = OsmWayNodeSerializer(source='way_nodes', many=True, read_only=True)

    class Meta:
        model = OsmWay
        fields = ('id', 'version', 'visible', 'timestamp', 'changeset', 'tags', 'nodes')
