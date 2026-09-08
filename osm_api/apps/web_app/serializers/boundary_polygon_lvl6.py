from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import BoundaryPolygonLvl6


class BoundaryPolygonLvl6Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = BoundaryPolygonLvl6
        geo_field = 'geom'
        fields = '__all__'
