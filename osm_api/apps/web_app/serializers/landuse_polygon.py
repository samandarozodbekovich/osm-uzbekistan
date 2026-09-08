from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import LandusePolygon


class LandusePolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = LandusePolygon
        geo_field = 'geom'
        fields = '__all__'
