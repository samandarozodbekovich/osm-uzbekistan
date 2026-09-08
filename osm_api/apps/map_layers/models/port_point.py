from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin
from .port_fields import _PortFields


class PortPoint(TrackingMixin, _PortFields):
    geom = models.MultiPointField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "port_point"
