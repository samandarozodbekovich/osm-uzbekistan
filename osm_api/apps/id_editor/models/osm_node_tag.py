from django.contrib.gis.db import models    

from .osm_node import OsmNode


class OsmNodeTag(models.Model):
    node = models.ForeignKey(OsmNode, on_delete=models.CASCADE, related_name='tags_set')
    k = models.CharField(max_length=255)
    v = models.TextField()

    class Meta:
        db_table = 'osm_node_tags'
        indexes = [models.Index(fields=['node'])]
        constraints = [
            models.UniqueConstraint(fields=['node', 'k'], name='uniq_node_tag_key'),
        ]