from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import (
    OsmNode, OsmWay, OsmRelation,
    OsmNodeTag, OsmWayTag, OsmWayNode,
    OsmRelationTag, OsmRelationMember,
)


class OsmNodeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmNodeTag
        fields = ('id', 'k', 'v')


class OsmWayTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmWayTag
        fields = ('id', 'k', 'v')


class OsmRelationTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmRelationTag
        fields = ('id', 'k', 'v')


class OsmWayNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmWayNode
        fields = ('sequence_id', 'node')


class OsmRelationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmRelationMember
        fields = ('sequence_id', 'member_type', 'member_id', 'role')


class OsmNodeSerializer(GeoFeatureModelSerializer):
    tags = OsmNodeTagSerializer(source='tags_set', many=True, read_only=True)

    class Meta:
        model = OsmNode
        geo_field = 'geom'
        fields = ('id', 'version', 'visible', 'lat', 'lon', 'timestamp', 'changeset', 'geom', 'tags')


class OsmWaySerializer(serializers.ModelSerializer):
    tags = OsmWayTagSerializer(source='tags_set', many=True, read_only=True)
    nodes = OsmWayNodeSerializer(source='way_nodes', many=True, read_only=True)

    class Meta:
        model = OsmWay
        fields = ('id', 'version', 'visible', 'timestamp', 'changeset', 'tags', 'nodes')


class OsmRelationSerializer(serializers.ModelSerializer):
    tags = OsmRelationTagSerializer(source='tags_set', many=True, read_only=True)
    members = OsmRelationMemberSerializer(many=True, read_only=True)

    class Meta:
        model = OsmRelation
        fields = ('id', 'version', 'visible', 'timestamp', 'changeset', 'tags', 'members')
