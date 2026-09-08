from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import WaterPolygon


class WaterPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = WaterPolygon
        geo_field = 'geom'
        fields = '__all__'
