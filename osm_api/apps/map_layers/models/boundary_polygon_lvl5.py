from .tracking_mixin import TrackingMixin
from .admin_boundary_fields import _AdminBoundaryFields


class BoundaryPolygonLvl5(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon_lvl5"
