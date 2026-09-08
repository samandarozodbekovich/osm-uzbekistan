from rest_framework import serializers

from ..models import OsmNodeTag


class OsmNodeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = OsmNodeTag
        fields = ('id', 'k', 'v')
