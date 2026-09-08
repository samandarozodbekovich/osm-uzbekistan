from ..models import VegetationPolygon
from ..serializers import VegetationPolygonSerializer
from .geo_layer_mixin import GeoLayerMixin


class VegetationPolygonViewSet(GeoLayerMixin):
    queryset = VegetationPolygon.objects.all()
    serializer_class = VegetationPolygonSerializer
