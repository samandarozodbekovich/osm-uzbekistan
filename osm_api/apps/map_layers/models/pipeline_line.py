from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class PipelineLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    substance = models.CharField(blank=True, null=True)
    location = models.CharField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    diameter = models.CharField(blank=True, null=True)
    pressure = models.CharField(blank=True, null=True)
    capacity = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pipeline_line"
