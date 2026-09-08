from ..models import RailwayLine
from ..serializers import RailwayLineSerializer
from .geo_layer_mixin import GeoLayerMixin


class RailwayLineViewSet(GeoLayerMixin):
    queryset = RailwayLine.objects.all()
    serializer_class = RailwayLineSerializer
    filterset_fields = ['railway']
