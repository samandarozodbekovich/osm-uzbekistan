"""
One typed model per NextGIS layer table, split one class per file.

Every table is managed = False: created by the NextGIS .sql dumps via
psql, never by Django migrations. Shared tracking columns come from
TrackingMixin (see add_layer_tracking_columns + fix_tracking_column_names).
"""

from .tracking_mixin import TrackingMixin
from .admin_boundary_fields import _AdminBoundaryFields
from .building_fields import _BuildingFields
from .poi_fields import _PoiFields
from .port_fields import _PortFields
from .settlement_fields import _SettlementFields

from .aerialway_line import AerialwayLine
from .aerialway_point import AerialwayPoint
from .airport_line import AirportLine
from .airport_polygon import AirportPolygon
from .boundary_polygon import BoundaryPolygon
from .boundary_polygon_lvl2 import BoundaryPolygonLvl2
from .boundary_polygon_lvl3 import BoundaryPolygonLvl3
from .boundary_polygon_lvl4 import BoundaryPolygonLvl4
from .boundary_polygon_lvl5 import BoundaryPolygonLvl5
from .boundary_polygon_lvl6 import BoundaryPolygonLvl6
from .boundary_polygon_lvl7 import BoundaryPolygonLvl7
from .boundary_polygon_lvl8 import BoundaryPolygonLvl8
from .boundary_polygon_lvl10 import BoundaryPolygonLvl10
from .building_point import BuildingPoint
from .building_polygon import BuildingPolygon
from .cutline_line import CutlineLine
from .elevation_line import ElevationLine
from .elevation_point import ElevationPoint
from .highway_crossing_point import HighwayCrossingPoint
from .highway_line import HighwayLine
from .island_polygon import IslandPolygon
from .land import Land
from .landuse_polygon import LandusePolygon
from .milestone_point import MilestonePoint
from .nature_reserve_polygon import NatureReservePolygon
from .parking_polygon import ParkingPolygon
from .pipeline_line import PipelineLine
from .poi_point import PoiPoint
from .poi_polygon import PoiPolygon
from .port_point import PortPoint
from .port_polygon import PortPolygon
from .power_line import PowerLine
from .power_point import PowerPoint
from .public_transport_line import PublicTransportLine
from .public_transport_point import PublicTransportPoint
from .railway_line import RailwayLine
from .railway_platform_polygon import RailwayPlatformPolygon
from .railway_station_point import RailwayStationPoint
from .settlement_point import SettlementPoint
from .settlement_polygon import SettlementPolygon
from .subway_entrance_point import SubwayEntrancePoint
from .surface_polygon import SurfacePolygon
from .vegetation_polygon import VegetationPolygon
from .water_line import WaterLine
from .water_point import WaterPoint
from .water_polygon import WaterPolygon

__all__ = [
    'TrackingMixin',
    '_AdminBoundaryFields',
    '_BuildingFields',
    '_PoiFields',
    '_PortFields',
    '_SettlementFields',
    'AerialwayLine',
    'AerialwayPoint',
    'AirportLine',
    'AirportPolygon',
    'BoundaryPolygon',
    'BoundaryPolygonLvl2',
    'BoundaryPolygonLvl3',
    'BoundaryPolygonLvl4',
    'BoundaryPolygonLvl5',
    'BoundaryPolygonLvl6',
    'BoundaryPolygonLvl7',
    'BoundaryPolygonLvl8',
    'BoundaryPolygonLvl10',
    'BuildingPoint',
    'BuildingPolygon',
    'CutlineLine',
    'ElevationLine',
    'ElevationPoint',
    'HighwayCrossingPoint',
    'HighwayLine',
    'IslandPolygon',
    'Land',
    'LandusePolygon',
    'MilestonePoint',
    'NatureReservePolygon',
    'ParkingPolygon',
    'PipelineLine',
    'PoiPoint',
    'PoiPolygon',
    'PortPoint',
    'PortPolygon',
    'PowerLine',
    'PowerPoint',
    'PublicTransportLine',
    'PublicTransportPoint',
    'RailwayLine',
    'RailwayPlatformPolygon',
    'RailwayStationPoint',
    'SettlementPoint',
    'SettlementPolygon',
    'SubwayEntrancePoint',
    'SurfacePolygon',
    'VegetationPolygon',
    'WaterLine',
    'WaterPoint',
    'WaterPolygon',
]
