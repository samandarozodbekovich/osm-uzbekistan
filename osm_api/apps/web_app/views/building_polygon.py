from ..models import BuildingPolygon
from ..serializers import BuildingPolygonSerializer
from .geo_layer_mixin import GeoLayerMixin


class BuildingPolygonViewSet(GeoLayerMixin):
    queryset = BuildingPolygon.objects.all()
    serializer_class = BuildingPolygonSerializer
