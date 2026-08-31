from django.contrib.gis.db import models

from .osm_relation import OsmRelation

class OsmRelationMember(models.Model):
    MEMBER_TYPES = (('node', 'node'), ('way', 'way'), ('relation', 'relation'))

    relation = models.ForeignKey(OsmRelation, on_delete=models.CASCADE, related_name='members')
    sequence_id = models.IntegerField()
    member_type = models.CharField(max_length=10, choices=MEMBER_TYPES)
    member_id = models.BigIntegerField()
    role = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'osm_relation_members'
        ordering = ['sequence_id']
        indexes = [
            models.Index(fields=['relation', 'sequence_id']),
            models.Index(fields=['member_type', 'member_id']),
        ]