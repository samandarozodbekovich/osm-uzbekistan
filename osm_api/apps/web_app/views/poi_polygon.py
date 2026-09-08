from ..models import PoiPolygon
from ..serializers import PoiPolygonSerializer
from .geo_layer_mixin import GeoLayerMixin


class PoiPolygonViewSet(GeoLayerMixin):
    queryset = PoiPolygon.objects.all()
    serializer_class = PoiPolygonSerializer
    filterset_fields = ['amenity', 'leisure', 'tourism']
