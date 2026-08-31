"""
apps/map_layers/models.py

46 real, typed models - one per NextGIS layer, generated from inspectdb
output and cleaned up to share tracking fields via TrackingMixin.

managed = False on every model: these tables were created directly by the
NextGIS .sql dumps (via psql), not by Django migrations. Django will never
try to create/alter/drop them - it only reads/writes rows.
"""

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


class AerialwayLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    aerialway = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "aerialway_line"


class AerialwayPoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    aerialway = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "aerialway_point"


class AirportLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    length = models.CharField(blank=True, null=True)
    ref = models.CharField(blank=True, null=True)
    width = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "airport_line"


class AirportPolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    aerod_type = models.CharField(blank=True, null=True)
    closest_to = models.CharField(blank=True, null=True)
    icao = models.CharField(blank=True, null=True)
    iata = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "airport_polygon"


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


class BoundaryPolygon(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon"


class BoundaryPolygonLvl2(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon_lvl2"


class BoundaryPolygonLvl3(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon_lvl3"


class BoundaryPolygonLvl4(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon_lvl4"


class BoundaryPolygonLvl5(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon_lvl5"


class BoundaryPolygonLvl6(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon_lvl6"


class BoundaryPolygonLvl7(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon_lvl7"


class BoundaryPolygonLvl8(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon_lvl8"


class BoundaryPolygonLvl10(TrackingMixin, _AdminBoundaryFields):
    class Meta:
        managed = False
        db_table = "boundary_polygon_lvl10"


class _BuildingFields(models.Model):
    fid = models.AutoField(primary_key=True)
    building = models.CharField(blank=True, null=True)
    addr_city = models.CharField(blank=True, null=True)
    a_strt = models.CharField(blank=True, null=True)
    a_sbrb = models.CharField(blank=True, null=True)
    a_hsnmbr = models.CharField(blank=True, null=True)
    a_place = models.CharField(blank=True, null=True)
    a_pstcd = models.CharField(blank=True, null=True)
    b_levels = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class BuildingPoint(TrackingMixin, _BuildingFields):
    geom = models.MultiPointField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "building_point"


class BuildingPolygon(TrackingMixin, _BuildingFields):
    geom = models.MultiPolygonField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "building_polygon"


class CutlineLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    cutline = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "cutline_line"


class ElevationLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    natural = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "elevation_line"


class ElevationPoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    natural = models.CharField(blank=True, null=True)
    ele = models.CharField(blank=True, null=True)
    mountain_p = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "elevation_point"


class HighwayCrossingPoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    highway = models.CharField(blank=True, null=True)
    crossing = models.CharField(blank=True, null=True)
    crossing_r = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "highway_crossing_point"


class HighwayLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    ref = models.CharField(blank=True, null=True)
    highway = models.CharField(blank=True, null=True)
    oneway = models.CharField(blank=True, null=True)
    bridge = models.CharField(blank=True, null=True)
    tunnel = models.CharField(blank=True, null=True)
    maxspeed = models.CharField(blank=True, null=True)
    lanes = models.CharField(blank=True, null=True)
    width = models.CharField(blank=True, null=True)
    surface = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "highway_line"


class IslandPolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    type = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "island_polygon"


class Land(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "land"


class LandusePolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    landuse = models.CharField(blank=True, null=True)
    rsdntl = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "landuse_polygon"


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


class NatureReservePolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    leisure = models.CharField(blank=True, null=True)
    boundary = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "nature_reserve_polygon"


class ParkingPolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    fee = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    parking = models.CharField(blank=True, null=True)
    access = models.CharField(blank=True, null=True)
    capacity = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "parking_polygon"


class PipelineLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    substance = models.CharField(blank=True, null=True)
    location = models.CharField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    diameter = models.CharField(blank=True, null=True)
    pressure = models.CharField(blank=True, null=True)
    capacity = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pipeline_line"


class _PoiFields(models.Model):
    fid = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    man_made = models.CharField(blank=True, null=True)
    leisure = models.CharField(blank=True, null=True)
    amenity = models.CharField(blank=True, null=True)
    office = models.CharField(blank=True, null=True)
    shop = models.CharField(blank=True, null=True)
    tourism = models.CharField(blank=True, null=True)
    sport = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class PoiPoint(TrackingMixin, _PoiFields):
    geom = models.MultiPointField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "poi_point"


class PoiPolygon(TrackingMixin, _PoiFields):
    geom = models.MultiPolygonField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "poi_polygon"


class _PortFields(models.Model):
    fid = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class PortPoint(TrackingMixin, _PortFields):
    geom = models.MultiPointField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "port_point"


class PortPolygon(TrackingMixin, _PortFields):
    geom = models.MultiPolygonField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "port_polygon"


class PowerLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    power = models.CharField(blank=True, null=True)
    voltage = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "power_line"


class PowerPoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    power = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "power_point"


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


class PublicTransportPoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    railway = models.CharField(blank=True, null=True)
    highway = models.CharField(blank=True, null=True)
    ref = models.CharField(blank=True, null=True)
    network = models.CharField(blank=True, null=True)
    public_tra = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "public_transport_point"


class RailwayLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    railway = models.CharField(blank=True, null=True)
    gauge = models.CharField(blank=True, null=True)
    service = models.CharField(blank=True, null=True)
    bridge = models.CharField(blank=True, null=True)
    tunnel = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "railway_line"


class RailwayPlatformPolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    railway = models.CharField(blank=True, null=True)
    ref = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "railway_platform_polygon"


class RailwayStationPoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    railway = models.CharField(blank=True, null=True)
    station = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "railway_station_point"


class _SettlementFields(models.Model):
    fid = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    int_name = models.CharField(blank=True, null=True)
    official_s = models.CharField(blank=True, null=True)
    place = models.CharField(blank=True, null=True)
    a_cntr = models.CharField(blank=True, null=True)
    a_rgn = models.CharField(blank=True, null=True)
    a_dstrct = models.CharField(blank=True, null=True)
    a_pstcd = models.CharField(blank=True, null=True)
    population = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class SettlementPoint(TrackingMixin, _SettlementFields):
    geom = models.MultiPointField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "settlement_point"


class SettlementPolygon(TrackingMixin, _SettlementFields):
    geom = models.MultiPolygonField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "settlement_polygon"


class SubwayEntrancePoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    railway = models.CharField(blank=True, null=True)
    network = models.CharField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    ref = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "subway_entrance_point"


class SurfacePolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    natural = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "surface_polygon"


class VegetationPolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    natural = models.CharField(blank=True, null=True)
    landuse = models.CharField(blank=True, null=True)
    wood = models.CharField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "vegetation_polygon"


class WaterLine(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiLineStringField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    waterway = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "water_line"


class WaterPoint(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPointField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    natural = models.CharField(blank=True, null=True)
    waterway = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "water_point"


class WaterPolygon(TrackingMixin):
    fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    name_en = models.CharField(blank=True, null=True)
    natural = models.CharField(blank=True, null=True)
    waterway = models.CharField(blank=True, null=True)
    wetland = models.CharField(blank=True, null=True)
    osm_type = models.CharField(blank=True, null=True)
    osm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "water_polygon"