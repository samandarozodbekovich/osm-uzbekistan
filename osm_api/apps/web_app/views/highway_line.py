from ..models import HighwayLine
from ..serializers import HighwayLineSerializer
from .geo_layer_mixin import GeoLayerMixin


class HighwayLineViewSet(GeoLayerMixin):
    queryset = HighwayLine.objects.all()
    serializer_class = HighwayLineSerializer
    filterset_fields = ['highway', 'oneway']
