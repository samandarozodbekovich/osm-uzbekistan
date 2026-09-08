from rest_framework.viewsets import ModelViewSet

from ..models import OsmWayTag
from ..serializers import OsmWayTagSerializer


class OsmWayTagViewSet(ModelViewSet):
    queryset = OsmWayTag.objects.all()
    serializer_class = OsmWayTagSerializer
    filterset_fields = ['way', 'k']
