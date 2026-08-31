from django.contrib.gis.geos import Polygon
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination

from .models import (
    BoundaryPolygonLvl2, BoundaryPolygonLvl4, BoundaryPolygonLvl6, BoundaryPolygonLvl8,
    BuildingPolygon, HighwayLine, LandusePolygon, ParkingPolygon,
    PoiPoint, PoiPolygon, RailwayLine,
    SettlementPoint, SettlementPolygon,
    VegetationPolygon, WaterLine, WaterPolygon,
)
from .serializers import (
    BoundaryPolygonLvl2Serializer, BoundaryPolygonLvl4Serializer,
    BoundaryPolygonLvl6Serializer, BoundaryPolygonLvl8Serializer,
    BuildingPolygonSerializer, HighwayLineSerializer, LandusePolygonSerializer,
    ParkingPolygonSerializer, PoiPointSerializer, PoiPolygonSerializer,
    RailwayLineSerializer, SettlementPointSerializer, SettlementPolygonSerializer,
    VegetationPolygonSerializer, WaterLineSerializer, WaterPolygonSerializer,
)


class GeoLayerPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class GeoLayerMixin(ReadOnlyModelViewSet):
    """Adds ?bbox=minx,miny,maxx,maxy filtering for all geo layers."""
    pagination_class = GeoLayerPagination

    def get_queryset(self):
        qs = super().get_queryset()
        bbox = self.request.query_params.get('bbox')
        if bbox:
            try:
                coords = [float(c) for c in bbox.split(',')]
                qs = qs.filter(geom__intersects=Polygon.from_bbox(coords))
            except (ValueError, TypeError):
                pass
        return qs


class BoundaryPolygonLvl2ViewSet(GeoLayerMixin):
    queryset = BoundaryPolygonLvl2.objects.all()
    serializer_class = BoundaryPolygonLvl2Serializer


class BoundaryPolygonLvl4ViewSet(GeoLayerMixin):
    queryset = BoundaryPolygonLvl4.objects.all()
    serializer_class = BoundaryPolygonLvl4Serializer


class BoundaryPolygonLvl6ViewSet(GeoLayerMixin):
    queryset = BoundaryPolygonLvl6.objects.all()
    serializer_class = BoundaryPolygonLvl6Serializer


class BoundaryPolygonLvl8ViewSet(GeoLayerMixin):
    queryset = BoundaryPolygonLvl8.objects.all()
    serializer_class = BoundaryPolygonLvl8Serializer


class BuildingPolygonViewSet(GeoLayerMixin):
    queryset = BuildingPolygon.objects.all()
    serializer_class = BuildingPolygonSerializer


class HighwayLineViewSet(GeoLayerMixin):
    queryset = HighwayLine.objects.all()
    serializer_class = HighwayLineSerializer
    filterset_fields = ['highway', 'oneway']


class LandusePolygonViewSet(GeoLayerMixin):
    queryset = LandusePolygon.objects.all()
    serializer_class = LandusePolygonSerializer
    filterset_fields = ['landuse']


class ParkingPolygonViewSet(GeoLayerMixin):
    queryset = ParkingPolygon.objects.all()
    serializer_class = ParkingPolygonSerializer
    filterset_fields = ['parking', 'access']


class PoiPointViewSet(GeoLayerMixin):
    queryset = PoiPoint.objects.all()
    serializer_class = PoiPointSerializer
    filterset_fields = ['amenity', 'leisure', 'tourism', 'shop']


class PoiPolygonViewSet(GeoLayerMixin):
    queryset = PoiPolygon.objects.all()
    serializer_class = PoiPolygonSerializer
    filterset_fields = ['amenity', 'leisure', 'tourism']


class RailwayLineViewSet(GeoLayerMixin):
    queryset = RailwayLine.objects.all()
    serializer_class = RailwayLineSerializer
    filterset_fields = ['railway']


class SettlementPointViewSet(GeoLayerMixin):
    queryset = SettlementPoint.objects.all()
    serializer_class = SettlementPointSerializer
    filterset_fields = ['place']


class SettlementPolygonViewSet(GeoLayerMixin):
    queryset = SettlementPolygon.objects.all()
    serializer_class = SettlementPolygonSerializer
    filterset_fields = ['place']


class VegetationPolygonViewSet(GeoLayerMixin):
    queryset = VegetationPolygon.objects.all()
    serializer_class = VegetationPolygonSerializer


class WaterLineViewSet(GeoLayerMixin):
    queryset = WaterLine.objects.all()
    serializer_class = WaterLineSerializer
    filterset_fields = ['waterway']


class WaterPolygonViewSet(GeoLayerMixin):
    queryset = WaterPolygon.objects.all()
    serializer_class = WaterPolygonSerializer
