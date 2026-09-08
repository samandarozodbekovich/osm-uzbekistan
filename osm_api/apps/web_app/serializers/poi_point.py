from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import PoiPoint


class PoiPointSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PoiPoint
        geo_field = 'geom'
        fields = '__all__'
