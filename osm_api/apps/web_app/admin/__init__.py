from .osm_changeset import OsmChangesetAdmin
from .osm_meta import OsmMetaAdmin
from .boundary_polygon_lvl2 import BoundaryPolygonLvl2Admin
from .boundary_polygon_lvl4 import BoundaryPolygonLvl4Admin
from .boundary_polygon_lvl6 import BoundaryPolygonLvl6Admin
from .boundary_polygon_lvl8 import BoundaryPolygonLvl8Admin
from .building_polygon import BuildingPolygonAdmin
from .highway_line import HighwayLineAdmin
from .landuse_polygon import LandusePolygonAdmin
from .parking_polygon import ParkingPolygonAdmin
from .poi_point import PoiPointAdmin
from .poi_polygon import PoiPolygonAdmin
from .railway_line import RailwayLineAdmin
from .settlement_point import SettlementPointAdmin
from .settlement_polygon import SettlementPolygonAdmin
from .vegetation_polygon import VegetationPolygonAdmin
from .water_line import WaterLineAdmin
from .water_polygon import WaterPolygonAdmin

__all__ = [
    'OsmChangesetAdmin',
    'OsmMetaAdmin',
    'BoundaryPolygonLvl2Admin',
    'BoundaryPolygonLvl4Admin',
    'BoundaryPolygonLvl6Admin',
    'BoundaryPolygonLvl8Admin',
    'BuildingPolygonAdmin',
    'HighwayLineAdmin',
    'LandusePolygonAdmin',
    'ParkingPolygonAdmin',
    'PoiPointAdmin',
    'PoiPolygonAdmin',
    'RailwayLineAdmin',
    'SettlementPointAdmin',
    'SettlementPolygonAdmin',
    'VegetationPolygonAdmin',
    'WaterLineAdmin',
    'WaterPolygonAdmin',
]
