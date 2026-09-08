from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import OsmNode
from .osm_node_tag import OsmNodeTagSerializer


class OsmNodeSerializer(GeoFeatureModelSerializer):
    tags = OsmNodeTagSerializer(source='tags_set', many=True, read_only=True)

    class Meta:
        model = OsmNode
        geo_field = 'geom'
        fields = ('id', 'version', 'visible', 'lat', 'lon', 'timestamp', 'changeset', 'geom', 'tags')
