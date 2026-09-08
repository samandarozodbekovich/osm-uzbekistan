from rest_framework.viewsets import ModelViewSet

from ..models import OsmNode
from ..serializers import OsmNodeSerializer
from .pagination import OsmPagination


class OsmNodeViewSet(ModelViewSet):
    queryset = OsmNode.objects.select_related('changeset').prefetch_related('tags_set')
    serializer_class = OsmNodeSerializer
    pagination_class = OsmPagination
    filterset_fields = ['visible', 'changeset']
