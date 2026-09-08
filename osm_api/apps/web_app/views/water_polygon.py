from ..models import WaterPolygon
from ..serializers import WaterPolygonSerializer
from .geo_layer_mixin import GeoLayerMixin


class WaterPolygonViewSet(GeoLayerMixin):
    queryset = WaterPolygon.objects.all()
    serializer_class = WaterPolygonSerializer
