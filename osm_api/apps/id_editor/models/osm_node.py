from django.contrib.gis.db import models    
from django.utils import timezone
from django.contrib.gis.geos import Point as _Point

from ...web_app.models import OsmChangeset


class OsmNode(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.IntegerField(default=1)
    visible = models.BooleanField(default=True)
    lat = models.FloatField()
    lon = models.FloatField()
    changeset = models.ForeignKey(
        OsmChangeset, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='nodes',
    )
    timestamp = models.DateTimeField(default=timezone.now)
    geom = models.PointField(srid=4326, blank=True, null=True)

    class Meta:
        db_table = 'osm_nodes'
        indexes = [models.Index(fields=['visible'])]

    def save(self, *args, **kwargs):
        self.geom = _Point(self.lon, self.lat, srid=4326)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"node/{self.id} v{self.version}"