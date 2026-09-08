from ..models import BoundaryPolygonLvl2
from ..serializers import BoundaryPolygonLvl2Serializer
from .geo_layer_mixin import GeoLayerMixin


class BoundaryPolygonLvl2ViewSet(GeoLayerMixin):
    queryset = BoundaryPolygonLvl2.objects.all()
    serializer_class = BoundaryPolygonLvl2Serializer
