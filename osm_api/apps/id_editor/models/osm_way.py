from django.contrib.gis.db import models    
from django.utils import timezone

from ...web_app.models import OsmChangeset


class OsmWay(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.IntegerField(default=1)
    visible = models.BooleanField(default=True)
    changeset = models.ForeignKey(
        OsmChangeset, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='ways',
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'osm_ways'

    def __str__(self):
        return f"way/{self.id} v{self.version}"