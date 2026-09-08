from ..models import SettlementPolygon
from ..serializers import SettlementPolygonSerializer
from .geo_layer_mixin import GeoLayerMixin


class SettlementPolygonViewSet(GeoLayerMixin):
    queryset = SettlementPolygon.objects.all()
    serializer_class = SettlementPolygonSerializer
    filterset_fields = ['place']
