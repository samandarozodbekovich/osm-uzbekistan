from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin
from .poi_fields import _PoiFields


class PoiPolygon(TrackingMixin, _PoiFields):
    geom = models.MultiPolygonField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "poi_polygon"
