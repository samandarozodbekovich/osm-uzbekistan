from rest_framework.routers import SimpleRouter
from .views import (
    OsmNodeViewSet, OsmWayViewSet, OsmRelationViewSet,
    OsmNodeTagViewSet, OsmWayTagViewSet, OsmWayNodeViewSet,
    OsmRelationTagViewSet, OsmRelationMemberViewSet,
)

router = SimpleRouter()
router.register('nodes', OsmNodeViewSet, basename='osm-node')
router.register('ways', OsmWayViewSet, basename='osm-way')
router.register('relations', OsmRelationViewSet, basename='osm-relation')
router.register('node-tags', OsmNodeTagViewSet, basename='osm-node-tag')
router.register('way-tags', OsmWayTagViewSet, basename='osm-way-tag')
router.register('way-nodes', OsmWayNodeViewSet, basename='osm-way-node')
router.register('relation-tags', OsmRelationTagViewSet, basename='osm-relation-tag')
router.register('relation-members', OsmRelationMemberViewSet, basename='osm-relation-member')

urlpatterns = router.urls

