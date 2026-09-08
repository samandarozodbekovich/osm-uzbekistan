from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import PoiPolygon


class PoiPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PoiPolygon
        geo_field = 'geom'
        fields = '__all__'
