from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import SettlementPolygon


class SettlementPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = SettlementPolygon
        geo_field = 'geom'
        fields = '__all__'
