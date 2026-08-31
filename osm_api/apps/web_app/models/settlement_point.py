from django.contrib.gis.db import models


class SettlementPoint(models.Model):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    name_en = models.CharField(max_length=255, blank=True, null=True)
    int_name = models.CharField(max_length=255, blank=True, null=True)
    official_s = models.CharField(max_length=255, blank=True, null=True)
    place = models.CharField(max_length=255, blank=True, null=True)
    a_cntr = models.CharField(max_length=255, blank=True, null=True)
    a_rgn = models.CharField(max_length=255, blank=True, null=True)
    a_dstrct = models.CharField(max_length=255, blank=True, null=True)
    a_pstcd = models.CharField(max_length=255, blank=True, null=True)
    population = models.CharField(max_length=255, blank=True, null=True)
    osm_type = models.CharField(max_length=20, blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'settlement_point'

    def __str__(self):
        return self.name or f"settlement_point #{self.fid}"
