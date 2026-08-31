from django.contrib.gis.db import models    


class HighwayLine(models.Model):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    name_en = models.CharField(max_length=255, blank=True, null=True)
    ref = models.CharField(max_length=255, blank=True, null=True)
    highway = models.CharField(max_length=255, blank=True, null=True)
    oneway = models.CharField(max_length=255, blank=True, null=True)
    bridge = models.CharField(max_length=255, blank=True, null=True)
    tunnel = models.CharField(max_length=255, blank=True, null=True)
    maxspeed = models.CharField(max_length=50, blank=True, null=True)
    lanes = models.CharField(max_length=50, blank=True, null=True)
    surface = models.CharField(max_length=100, blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'highway_line'