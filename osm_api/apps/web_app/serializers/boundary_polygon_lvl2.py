from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import BoundaryPolygonLvl2


class BoundaryPolygonLvl2Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = BoundaryPolygonLvl2
        geo_field = 'geom'
        fields = '__all__'
