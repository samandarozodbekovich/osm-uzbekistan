from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class Land(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "land"
