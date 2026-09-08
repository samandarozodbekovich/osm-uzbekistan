from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class AirportPolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    aerod_type = models.CharField(blank=True, null=True)
    closest_to = models.CharField(blank=True, null=True)
    icao = models.CharField(blank=True, null=True)
    iata = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "airport_polygon"
