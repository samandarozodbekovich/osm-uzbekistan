from ..models import BoundaryPolygonLvl4
from ..serializers import BoundaryPolygonLvl4Serializer
from .geo_layer_mixin import GeoLayerMixin


class BoundaryPolygonLvl4ViewSet(GeoLayerMixin):
    queryset = BoundaryPolygonLvl4.objects.all()
    serializer_class = BoundaryPolygonLvl4Serializer
