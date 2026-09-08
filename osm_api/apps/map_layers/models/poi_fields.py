from django.contrib.gis.db import models


class _PoiFields(models.Model):
    fid = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    man_made = models.CharField(blank=True, null=True)
    leisure = models.CharField(blank=True, null=True)
    amenity = models.CharField(blank=True, null=True)
    office = models.CharField(blank=True, null=True)
    shop = models.CharField(blank=True, null=True)
    tourism = models.CharField(blank=True, null=True)
    sport = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        abstract = True
