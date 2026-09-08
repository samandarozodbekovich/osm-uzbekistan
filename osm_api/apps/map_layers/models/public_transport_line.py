from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin


class PublicTransportLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    route = models.CharField(blank=True, null=True)
    ref = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    from_field = models.CharField(db_column="from", blank=True, null=True)  # "from" is a Python reserved word
    to = models.CharField(blank=True, null=True)
    via = models.CharField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    network = models.CharField(blank=True, null=True)
    note = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "public_transport_line"
