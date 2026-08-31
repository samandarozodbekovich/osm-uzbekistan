from django.contrib.gis.db import models


class PoiPoint(models.Model):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
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
        db_table = 'poi_point'

    def tags(self):
        result = {}
        for key, field in TAG_FIELD_MAP.items():
            value = getattr(self, field)
            if value:
                result[key] = value
        return result

    def __str__(self):
        return self.name or f"poi_point #{self.fid}"
    
    
TAG_FIELD_MAP = {
    'name': 'name',
    'name:en': 'name_en',
    'man_made': 'man_made',
    'leisure': 'leisure',
    'amenity': 'amenity',
    'office': 'office',
    'shop': 'shop',
    'tourism': 'tourism',
    'sport': 'sport',
}