from rest_framework.viewsets import ModelViewSet

from ..models import OsmRelation
from ..serializers import OsmRelationSerializer
from .pagination import OsmPagination


class OsmRelationViewSet(ModelViewSet):
    queryset = OsmRelation.objects.select_related('changeset').prefetch_related('tags_set', 'members')
    serializer_class = OsmRelationSerializer
    pagination_class = OsmPagination
    filterset_fields = ['visible', 'changeset']
