from rest_framework.viewsets import ModelViewSet

from ..models import OsmNodeTag
from ..serializers import OsmNodeTagSerializer


class OsmNodeTagViewSet(ModelViewSet):
    queryset = OsmNodeTag.objects.all()
    serializer_class = OsmNodeTagSerializer
    filterset_fields = ['node', 'k']
