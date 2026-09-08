from rest_framework.viewsets import ModelViewSet

from ..models import OsmRelationMember
from ..serializers import OsmRelationMemberSerializer


class OsmRelationMemberViewSet(ModelViewSet):
    queryset = OsmRelationMember.objects.all()
    serializer_class = OsmRelationMemberSerializer
    filterset_fields = ['relation', 'member_type']
