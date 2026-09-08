from rest_framework.viewsets import ModelViewSet

from ..models import OsmWay
from ..serializers import OsmWaySerializer
from .pagination import OsmPagination


class OsmWayViewSet(ModelViewSet):
    queryset = OsmWay.objects.select_related('changeset').prefetch_related('tags_set', 'way_nodes')
    serializer_class = OsmWaySerializer
    pagination_class = OsmPagination
    filterset_fields = ['visible', 'changeset']
