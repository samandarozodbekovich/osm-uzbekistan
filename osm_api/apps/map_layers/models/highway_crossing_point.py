from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class HighwayCrossingPoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    highway = models.CharField(blank=True, null=True)
    crossing = models.CharField(blank=True, null=True)
    crossing_r = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "highway_crossing_point"
