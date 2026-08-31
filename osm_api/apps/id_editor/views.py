from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination

from .models import (
    OsmNode, OsmWay, OsmRelation,
    OsmNodeTag, OsmWayTag, OsmWayNode,
    OsmRelationTag, OsmRelationMember,
)
from .serializers import (
    OsmNodeSerializer, OsmWaySerializer, OsmRelationSerializer,
    OsmNodeTagSerializer, OsmWayTagSerializer, OsmWayNodeSerializer,
    OsmRelationTagSerializer, OsmRelationMemberSerializer,
)


class OsmPagination(PageNumberPagination):
    page_size = 200
    page_size_query_param = 'page_size'
    max_page_size = 2000


class OsmNodeViewSet(ModelViewSet):
    queryset = OsmNode.objects.select_related('changeset').prefetch_related('tags_set')
    serializer_class = OsmNodeSerializer
    pagination_class = OsmPagination
    filterset_fields = ['visible', 'changeset']


class OsmWayViewSet(ModelViewSet):
    queryset = OsmWay.objects.select_related('changeset').prefetch_related('tags_set', 'way_nodes')
    serializer_class = OsmWaySerializer
    pagination_class = OsmPagination
    filterset_fields = ['visible', 'changeset']


class OsmRelationViewSet(ModelViewSet):
    queryset = OsmRelation.objects.select_related('changeset').prefetch_related('tags_set', 'members')
    serializer_class = OsmRelationSerializer
    pagination_class = OsmPagination
    filterset_fields = ['visible', 'changeset']


class OsmNodeTagViewSet(ModelViewSet):
    queryset = OsmNodeTag.objects.all()
    serializer_class = OsmNodeTagSerializer
    filterset_fields = ['node', 'k']


class OsmWayTagViewSet(ModelViewSet):
    queryset = OsmWayTag.objects.all()
    serializer_class = OsmWayTagSerializer
    filterset_fields = ['way', 'k']


class OsmWayNodeViewSet(ReadOnlyModelViewSet):
    queryset = OsmWayNode.objects.all()
    serializer_class = OsmWayNodeSerializer
    filterset_fields = ['way', 'node']


class OsmRelationTagViewSet(ModelViewSet):
    queryset = OsmRelationTag.objects.all()
    serializer_class = OsmRelationTagSerializer
    filterset_fields = ['relation', 'k']


class OsmRelationMemberViewSet(ModelViewSet):
    queryset = OsmRelationMember.objects.all()
    serializer_class = OsmRelationMemberSerializer
    filterset_fields = ['relation', 'member_type']
