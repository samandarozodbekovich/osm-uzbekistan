from django.contrib.gis.db import models


class PoiPolygon(models.Model):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    name_en = models.CharField(max_length=255, blank=True, null=True)
    man_made = models.CharField(max_length=255, blank=True, null=True)
    leisure = models.CharField(max_length=255, blank=True, null=True)
    amenity = models.CharField(max_length=255, blank=True, null=True)
    office = models.CharField(max_length=255, blank=True, null=True)
    shop = models.CharField(max_length=255, blank=True, null=True)
    tourism = models.CharField(max_length=255, blank=True, null=True)
    sport = models.CharField(max_length=255, blank=True, null=True)
    osm_type = models.CharField(max_length=20, blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'poi_polygon'

    def __str__(self):
        return self.name or f"poi_polygon #{self.fid}"
