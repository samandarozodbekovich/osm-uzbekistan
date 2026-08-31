from django.contrib.gis.db import models    


class RailwayLine(models.Model):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    railway = models.CharField(max_length=255, blank=True, null=True)
    bridge = models.CharField(max_length=255, blank=True, null=True)
    tunnel = models.CharField(max_length=255, blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'railway_line'