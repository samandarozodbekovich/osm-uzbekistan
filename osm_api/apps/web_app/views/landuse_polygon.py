from ..models import LandusePolygon
from ..serializers import LandusePolygonSerializer
from .geo_layer_mixin import GeoLayerMixin


class LandusePolygonViewSet(GeoLayerMixin):
    queryset = LandusePolygon.objects.all()
    serializer_class = LandusePolygonSerializer
    filterset_fields = ['landuse']
