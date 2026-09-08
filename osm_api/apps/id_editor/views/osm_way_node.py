from rest_framework.viewsets import ReadOnlyModelViewSet

from ..models import OsmWayNode
from ..serializers import OsmWayNodeSerializer


class OsmWayNodeViewSet(ReadOnlyModelViewSet):
    queryset = OsmWayNode.objects.all()
    serializer_class = OsmWayNodeSerializer
    filterset_fields = ['way', 'node']
