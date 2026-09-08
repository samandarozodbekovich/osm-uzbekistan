from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class VegetationPolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    natural = models.CharField(blank=True, null=True)
    landuse = models.CharField(blank=True, null=True)
    wood = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "vegetation_polygon"
