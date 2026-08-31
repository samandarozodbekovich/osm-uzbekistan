from django.contrib.gis.db import models    


class BoundaryPolygonLvl8(models.Model):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    name_en = models.CharField(max_length=255, blank=True, null=True)
    admin_lvl = models.CharField(max_length=20, blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'boundary_polygon_lvl8'