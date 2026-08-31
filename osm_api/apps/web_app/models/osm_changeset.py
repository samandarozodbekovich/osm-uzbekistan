from django.utils import timezone
from django.db import models
    

class OsmChangeset(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.CharField(max_length=255, default='anonymous')
    uid = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(blank=True, null=True)
    open = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'osm_changeset'
