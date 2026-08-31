from django.contrib.gis.db import models

from .osm_relation import OsmRelation


class OsmRelationTag(models.Model):
    relation = models.ForeignKey(OsmRelation, on_delete=models.CASCADE, related_name='tags_set')
    k = models.CharField(max_length=255)
    v = models.TextField()

    class Meta:
        db_table = 'osm_relation_tags'
        indexes = [models.Index(fields=['relation'])]
        constraints = [
            models.UniqueConstraint(fields=['relation', 'k'], name='uniq_relation_tag_key'),
        ]