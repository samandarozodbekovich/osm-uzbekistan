from django.contrib.gis.db import models
from .tracking_mixin import TrackingMixin
from .building_fields import _BuildingFields


class BuildingPolygon(TrackingMixin, _BuildingFields):
    geom = models.MultiPolygonField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "building_polygon"
