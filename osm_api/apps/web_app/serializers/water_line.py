from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import WaterLine


class WaterLineSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = WaterLine
        geo_field = 'geom'
        fields = '__all__'
