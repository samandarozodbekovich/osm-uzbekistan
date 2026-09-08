from django.contrib.gis.db import models


class _SettlementFields(models.Model):
    fid = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    int_name = models.CharField(blank=True, null=True)
    official_s = models.CharField(blank=True, null=True)
    place = models.CharField(blank=True, null=True)
    a_cntr = models.CharField(blank=True, null=True)
    a_rgn = models.CharField(blank=True, null=True)
    a_dstrct = models.CharField(blank=True, null=True)
    a_pstcd = models.CharField(blank=True, null=True)
    population = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        abstract = True
