from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin
from .poi_fields import _PoiFields


class PoiPoint(TrackingMixin, _PoiFields):
    geom = models.MultiPointField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "poi_point"
