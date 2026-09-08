from rest_framework.viewsets import ModelViewSet

from ..models import OsmRelationTag
from ..serializers import OsmRelationTagSerializer


class OsmRelationTagViewSet(ModelViewSet):
    queryset = OsmRelationTag.objects.all()
    serializer_class = OsmRelationTagSerializer
    filterset_fields = ['relation', 'k']
