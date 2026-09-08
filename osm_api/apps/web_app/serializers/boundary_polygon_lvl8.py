from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import BoundaryPolygonLvl8


class BoundaryPolygonLvl8Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = BoundaryPolygonLvl8
        geo_field = 'geom'
        fields = '__all__'
