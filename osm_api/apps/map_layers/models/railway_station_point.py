from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class RailwayStationPoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    railway = models.CharField(blank=True, null=True)
    station = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "railway_station_point"
