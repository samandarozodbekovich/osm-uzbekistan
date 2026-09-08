from ..models import ParkingPolygon
from ..serializers import ParkingPolygonSerializer
from .geo_layer_mixin import GeoLayerMixin


class ParkingPolygonViewSet(GeoLayerMixin):
    queryset = ParkingPolygon.objects.all()
    serializer_class = ParkingPolygonSerializer
    filterset_fields = ['parking', 'access']
