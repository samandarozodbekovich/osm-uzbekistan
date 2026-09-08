from ..models import BoundaryPolygonLvl6
from ..serializers import BoundaryPolygonLvl6Serializer
from .geo_layer_mixin import GeoLayerMixin


class BoundaryPolygonLvl6ViewSet(GeoLayerMixin):
    queryset = BoundaryPolygonLvl6.objects.all()
    serializer_class = BoundaryPolygonLvl6Serializer
