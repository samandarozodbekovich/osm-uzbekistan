from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import SettlementPoint


class SettlementPointSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = SettlementPoint
        geo_field = 'geom'
        fields = '__all__'
