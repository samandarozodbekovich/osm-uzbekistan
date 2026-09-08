from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class HighwayLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    ref = models.CharField(blank=True, null=True)
    highway = models.CharField(blank=True, null=True)
    oneway = models.CharField(blank=True, null=True)
    bridge = models.CharField(blank=True, null=True)
    tunnel = models.CharField(blank=True, null=True)
    maxspeed = models.CharField(blank=True, null=True)
    lanes = models.CharField(blank=True, null=True)
    width = models.CharField(blank=True, null=True)
    surface = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "highway_line"
