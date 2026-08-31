from rest_framework.routers import SimpleRouter
from .views import (
    BoundaryPolygonLvl2ViewSet, BoundaryPolygonLvl4ViewSet,
    BoundaryPolygonLvl6ViewSet, BoundaryPolygonLvl8ViewSet,
    BuildingPolygonViewSet, HighwayLineViewSet, LandusePolygonViewSet,
    ParkingPolygonViewSet, PoiPointViewSet, PoiPolygonViewSet,
    RailwayLineViewSet, SettlementPointViewSet, SettlementPolygonViewSet,
    VegetationPolygonViewSet, WaterLineViewSet, WaterPolygonViewSet,
)

router = SimpleRouter()
router.register('boundaries/lvl2', BoundaryPolygonLvl2ViewSet, basename='boundary-lvl2')
router.register('boundaries/lvl4', BoundaryPolygonLvl4ViewSet, basename='boundary-lvl4')
router.register('boundaries/lvl6', BoundaryPolygonLvl6ViewSet, basename='boundary-lvl6')
router.register('boundaries/lvl8', BoundaryPolygonLvl8ViewSet, basename='boundary-lvl8')
router.register('buildings', BuildingPolygonViewSet, basename='building')
router.register('highways', HighwayLineViewSet, basename='highway')
router.register('landuse', LandusePolygonViewSet, basename='landuse')
router.register('parking', ParkingPolygonViewSet, basename='parking')
router.register('pois/points', PoiPointViewSet, basename='poi-point')
router.register('pois/polygons', PoiPolygonViewSet, basename='poi-polygon')
router.register('railways', RailwayLineViewSet, basename='railway')
router.register('settlements/points', SettlementPointViewSet, basename='settlement-point')
router.register('settlements/polygons', SettlementPolygonViewSet, basename='settlement-polygon')
router.register('vegetation', VegetationPolygonViewSet, basename='vegetation')
router.register('water/lines', WaterLineViewSet, basename='water-line')
router.register('water/polygons', WaterPolygonViewSet, basename='water-polygon')

urlpatterns = router.urls

