from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import ParkingPolygon


class ParkingPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = ParkingPolygon
        geo_field = 'geom'
        fields = '__all__'
