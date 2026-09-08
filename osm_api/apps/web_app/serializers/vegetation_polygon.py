from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import VegetationPolygon


class VegetationPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = VegetationPolygon
        geo_field = 'geom'
        fields = '__all__'
