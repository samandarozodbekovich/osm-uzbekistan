from ..models import PoiPoint
from ..serializers import PoiPointSerializer
from .geo_layer_mixin import GeoLayerMixin


class PoiPointViewSet(GeoLayerMixin):
    queryset = PoiPoint.objects.all()
    serializer_class = PoiPointSerializer
    filterset_fields = ['amenity', 'leisure', 'tourism', 'shop']
