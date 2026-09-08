from django.conf import settings
from django.contrib.gis.db import models


class TrackingMixin(models.Model):
    """
    Shared editing/tracking fields, added to every layer table via
    add_layer_tracking_columns + fix_tracking_column_names.

    NOTE: named "edit_source" (not "source") because some NextGIS layers
    (e.g. milestone_point) already have their own native "source" field.
    """
    edit_source = models.CharField(max_length=50, default="nextgis", db_column="edit_source")
    version = models.IntegerField(default=1)
    needs_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        db_column="updated_by_id", db_constraint=False,
    )

    class Meta:
        abstract = True
