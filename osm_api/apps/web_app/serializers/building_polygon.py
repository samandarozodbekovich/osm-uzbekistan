from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import BuildingPolygon


class BuildingPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = BuildingPolygon
        geo_field = 'geom'
        fields = '__all__'
