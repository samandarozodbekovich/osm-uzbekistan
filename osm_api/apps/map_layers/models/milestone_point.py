from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class MilestonePoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    distance = models.CharField(blank=True, null=True)
    # NextGIS's own "source" attribute (e.g. survey/GPS provenance of the
    # milestone) - distinct from TrackingMixin.edit_source, no collision.
    source = models.CharField(blank=True, null=True)
    check_date = models.CharField(blank=True, null=True)
    pk_bkwrd = models.CharField(blank=True, null=True)
    dist_bkwrd = models.CharField(blank=True, null=True)
    dist_frwrd = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "milestone_point"
