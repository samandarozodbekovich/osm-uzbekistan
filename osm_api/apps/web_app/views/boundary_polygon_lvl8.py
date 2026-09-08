from ..models import BoundaryPolygonLvl8
from ..serializers import BoundaryPolygonLvl8Serializer
from .geo_layer_mixin import GeoLayerMixin


class BoundaryPolygonLvl8ViewSet(GeoLayerMixin):
    queryset = BoundaryPolygonLvl8.objects.all()
    serializer_class = BoundaryPolygonLvl8Serializer
