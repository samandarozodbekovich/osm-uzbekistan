from django.contrib.gis.geos import Polygon
from rest_framework.viewsets import ReadOnlyModelViewSet

from .pagination import GeoLayerPagination


class GeoLayerMixin(ReadOnlyModelViewSet):
    """Adds ?bbox=minx,miny,maxx,maxy filtering for all geo layers."""
    pagination_class = GeoLayerPagination

    def get_queryset(self):
        qs = super().get_queryset()
        bbox = self.request.query_params.get('bbox')
        if bbox:
            try:
                coords = [float(c) for c in bbox.split(',')]
                qs = qs.filter(geom__intersects=Polygon.from_bbox(coords))
            except (ValueError, TypeError):
                pass
        return qs
