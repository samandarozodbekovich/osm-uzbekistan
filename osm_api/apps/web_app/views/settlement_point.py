from ..models import SettlementPoint
from ..serializers import SettlementPointSerializer
from .geo_layer_mixin import GeoLayerMixin


class SettlementPointViewSet(GeoLayerMixin):
    queryset = SettlementPoint.objects.all()
    serializer_class = SettlementPointSerializer
    filterset_fields = ['place']
