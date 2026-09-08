from django.contrib.gis.db import models


class _AdminBoundaryFields(models.Model):
    """Shared field set for boundary_polygon + all boundary_polygon_lvlN tables."""
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    admin_lvl = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)
    admin_l1d = models.BigIntegerField(blank=True, null=True)
    admin_l1 = models.CharField(max_length=128, blank=True, null=True)
    admin_l2d = models.BigIntegerField(blank=True, null=True)
    admin_l2 = models.CharField(max_length=128, blank=True, null=True)
    admin_l3d = models.BigIntegerField(blank=True, null=True)
    admin_l3 = models.CharField(max_length=128, blank=True, null=True)
    admin_l4d = models.BigIntegerField(blank=True, null=True)
    admin_l4 = models.CharField(max_length=128, blank=True, null=True)
    admin_l5d = models.BigIntegerField(blank=True, null=True)
    admin_l5 = models.CharField(max_length=128, blank=True, null=True)
    admin_l6d = models.BigIntegerField(blank=True, null=True)
    admin_l6 = models.CharField(max_length=128, blank=True, null=True)
    admin_l7d = models.BigIntegerField(blank=True, null=True)
    admin_l7 = models.CharField(max_length=128, blank=True, null=True)
    admin_l8d = models.BigIntegerField(blank=True, null=True)
    admin_l8 = models.CharField(max_length=128, blank=True, null=True)
    admin_l9d = models.BigIntegerField(blank=True, null=True)
    admin_l9 = models.CharField(max_length=128, blank=True, null=True)
    admin_l10d = models.BigIntegerField(blank=True, null=True)
    admin_l10 = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        abstract = True
