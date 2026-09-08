from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import RailwayLine


class RailwayLineSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = RailwayLine
        geo_field = 'geom'
        fields = '__all__'
