from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin
from .settlement_fields import _SettlementFields


class SettlementPoint(TrackingMixin, _SettlementFields):
    geom = models.MultiPointField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "settlement_point"
