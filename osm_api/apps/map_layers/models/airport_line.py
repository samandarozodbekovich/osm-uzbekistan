from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class AirportLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    length = models.CharField(blank=True, null=True)
    ref = models.CharField(blank=True, null=True)
    width = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "airport_line"
