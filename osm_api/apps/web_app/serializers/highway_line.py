from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import HighwayLine


class HighwayLineSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = HighwayLine
        geo_field = 'geom'
        fields = '__all__'
