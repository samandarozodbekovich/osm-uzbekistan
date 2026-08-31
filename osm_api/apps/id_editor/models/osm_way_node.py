from django.contrib.gis.db import models    

from .osm_way import OsmWay
from .osm_node import OsmNode


class OsmWayNode(models.Model):
    way = models.ForeignKey(OsmWay, on_delete=models.CASCADE, related_name='way_nodes')
    sequence_id = models.IntegerField()
    node = models.ForeignKey(OsmNode, on_delete=models.CASCADE, related_name='+')

    class Meta:
        db_table = 'osm_way_nodes'
        ordering = ['sequence_id']
        indexes = [
            models.Index(fields=['way', 'sequence_id']),
            models.Index(fields=['node']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['way', 'sequence_id'], name='uniq_way_seq'),
        ]