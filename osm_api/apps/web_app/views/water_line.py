from ..models import WaterLine
from ..serializers import WaterLineSerializer
from .geo_layer_mixin import GeoLayerMixin


class WaterLineViewSet(GeoLayerMixin):
    queryset = WaterLine.objects.all()
    serializer_class = WaterLineSerializer
    filterset_fields = ['waterway']
