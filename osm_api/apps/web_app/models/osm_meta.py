from django.db import models
from django.utils import timezone

from .osm_changeset import OsmChangeset

class OsmMeta(models.Model):
    osm_id = models.BigIntegerField(primary_key=True)
    osm_type = models.CharField(max_length=20, default='node')
    version = models.IntegerField(default=1)
    changeset = models.ForeignKey(
        OsmChangeset, on_delete=models.SET_NULL, blank=True, null=True
    )
    uid = models.IntegerField(default=1)
    user = models.CharField(max_length=255, default='anonymous')
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'osm_meta'