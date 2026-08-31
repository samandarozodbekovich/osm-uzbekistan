from django.contrib.gis.db import models    

from .osm_way import OsmWay


class OsmWayTag(models.Model):
    way = models.ForeignKey(OsmWay, on_delete=models.CASCADE, related_name='tags_set')
    k = models.CharField(max_length=255)
    v = models.TextField()

    class Meta:
        db_table = 'osm_way_tags'
        indexes = [models.Index(fields=['way'])]
        constraints = [
            models.UniqueConstraint(fields=['way', 'k'], name='uniq_way_tag_key'),
        ]