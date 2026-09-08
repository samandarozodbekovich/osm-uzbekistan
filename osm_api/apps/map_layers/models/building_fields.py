from django.contrib.gis.db import models


class _BuildingFields(models.Model):
    fid = models.AutoField(primary_key=True)
    building = models.CharField(blank=True, null=True)
    addr_city = models.CharField(blank=True, null=True)
    a_strt = models.CharField(blank=True, null=True)
    a_sbrb = models.CharField(blank=True, null=True)
    a_hsnmbr = models.CharField(blank=True, null=True)
    a_place = models.CharField(blank=True, null=True)
    a_pstcd = models.CharField(blank=True, null=True)
    b_levels = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        abstract = True
