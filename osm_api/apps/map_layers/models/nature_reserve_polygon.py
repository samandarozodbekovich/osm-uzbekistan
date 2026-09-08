from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class NatureReservePolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    leisure = models.CharField(blank=True, null=True)
    boundary = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "nature_reserve_polygon"
