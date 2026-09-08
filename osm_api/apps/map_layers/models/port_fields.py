from django.contrib.gis.db import models


class _PortFields(models.Model):
    fid = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        abstract = True
