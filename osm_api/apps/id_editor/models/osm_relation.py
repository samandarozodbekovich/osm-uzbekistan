from django.contrib.gis.db import models    
from django.utils import timezone

from ...web_app.models import OsmChangeset


class OsmRelation(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.IntegerField(default=1)
    visible = models.BooleanField(default=True)
    changeset = models.ForeignKey(
        OsmChangeset, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='relations',
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'osm_relations'

    def __str__(self):
        return f"relation/{self.id} v{self.version}"