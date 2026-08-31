from .osm_node import OsmNodeAdmin
from .osm_node_tag import OsmNodeTagAdmin
from .osm_way import OsmWayAdmin
from .osm_way_tag import OsmWayTagAdmin
from .osm_way_node import OsmWayNodeAdmin
from .osm_relation import OsmRelationAdmin
from .osm_relation_tag import OsmRelationTagAdmin
from .osm_relation_member import OsmRelationMemberAdmin

__all__ = [
    'OsmNodeAdmin',
    'OsmNodeTagAdmin',
    'OsmWayAdmin',
    'OsmWayTagAdmin',
    'OsmWayNodeAdmin',
    'OsmRelationAdmin',
    'OsmRelationTagAdmin',
    'OsmRelationMemberAdmin',
]
