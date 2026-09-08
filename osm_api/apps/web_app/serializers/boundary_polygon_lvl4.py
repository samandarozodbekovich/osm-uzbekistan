from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import BoundaryPolygonLvl4


class BoundaryPolygonLvl4Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = BoundaryPolygonLvl4
        geo_field = 'geom'
        fields = '__all__'
