from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin
from .settlement_fields import _SettlementFields


class SettlementPolygon(TrackingMixin, _SettlementFields):
    geom = models.MultiPolygonField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "settlement_polygon"
