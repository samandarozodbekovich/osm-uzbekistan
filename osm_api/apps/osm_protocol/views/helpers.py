"""
Shared constants and helper functions for the OSM API v0.6 emulation views.

The ID-namespacing scheme lets a single set of integer IDs address three
different kinds of element:

  Point/way IDs:   (table_idx + 1) * 10^9 + fid*100 + sub_geom_idx
      max ≈ 46 * 1B + 1M*100 = 46B + 100M ≈ 46B
  Vertex node IDs: VERTEX_BASE + table_idx*200B + fid*100K + part_i*10K + vertex_seq
      max ≈ 10T + 46*200B + 1M*100K = 10T + 9.2T + 100B ≈ 19.3T
  User-edit IDs (osm_nodes/osm_ways): regular small DB ids (< 1B)

  All ranges: user-edits < 1B << layer IDs ~46B << vertex IDs ~10T << JS safe int ~9e15
"""

import inspect

from django.contrib.gis.db.models import (
    MultiPointField, MultiLineStringField, MultiPolygonField,
    PointField, LineStringField, PolygonField,
)
from django.contrib.gis.geos import Polygon
from django.utils import timezone

from apps.id_editor.models import (
    OsmNode, OsmWay, OsmWayNode, OsmNodeTag, OsmWayTag,
)
import apps.map_layers.models as _layer_models

_LAYER_ID_BASE  = 1_000_000_000          # (table_idx+1) * this
_VERTEX_BASE    = 10_000_000_000_000     # synthetic vertex nodes for ways
_VTX_TABLE_STRIDE = 200_000_000_000     # per-table stride in vertex namespace (200B)
_VTX_FEAT_STRIDE  = 100_000            # per-feature vertex slots (fid * this)
_VTX_PART_STRIDE  = 10_000             # per-geometry-part vertex slots

# Tables too large/complex to serve as editing ways (admin boundaries, land mask).
# These are shown via Martin vector tiles; iD doesn't need to edit them as raw ways.
_SKIP_EDITING = frozenset({
    'boundary_polygon', 'boundary_polygon_lvl2', 'boundary_polygon_lvl3',
    'boundary_polygon_lvl4', 'boundary_polygon_lvl5', 'boundary_polygon_lvl6',
    'boundary_polygon_lvl7', 'boundary_polygon_lvl8', 'boundary_polygon_lvl10',
    'land',
})

# If a feature's own bounding box is more than this many times larger than the
# request bbox, it's probably a region-scale polygon — skip it.
_MAX_FEATURE_BBOX_RATIO = 20

# Fields never shown as OSM tags
_SKIP = frozenset({
    'fid', 'geom', 'osm_type',
    'edit_source', 'version', 'needs_review',
    'created_at', 'updated_at', 'updated_by', 'updated_by_id',
})

# NextGIS abbreviated names → OSM tag keys
_REMAP = {
    'a_strt':     'addr:street',
    'a_sbrb':     'addr:suburb',
    'a_hsnmbr':   'addr:housenumber',
    'a_place':    'addr:place',
    'a_pstcd':    'addr:postcode',
    'b_levels':   'building:levels',
    'name_en':    'name:en',
    'aerod_type': 'aerodrome:type',
    'mountain_p': 'mountain_pass',
    'crossing_r': 'crossing:ref',
    'admin_lvl':  'admin_level',
    'rsdntl':     'residential',
    'public_tra': 'public_transport',
    'from_field': 'from',
}


# All 46 concrete layer models, sorted for stable table_idx
def _discover_layer_models():
    result = []
    for _, obj in inspect.getmembers(_layer_models, inspect.isclass):
        if (issubclass(obj, _layer_models.TrackingMixin)
                and obj is not _layer_models.TrackingMixin
                and not obj._meta.abstract):
            result.append(obj)
    return sorted(result, key=lambda m: m._meta.db_table)


_LAYER_MODELS = _discover_layer_models()


def _geom_kind(model):
    try:
        f = model._meta.get_field('geom')
    except Exception:
        return None
    if isinstance(f, (MultiPointField, PointField)):
        return 'point'
    if isinstance(f, (MultiLineStringField, LineStringField)):
        return 'line'
    if isinstance(f, (MultiPolygonField, PolygonField)):
        return 'polygon'
    return None


def _tag_fields(model):
    result = []
    for field in model._meta.fields:
        name = field.name
        if name in _SKIP:
            continue
        if getattr(field, 'related_model', None) is not None:
            continue
        result.append((name, _REMAP.get(name, name)))
    return result


def _feat_tags(feat, tag_fields):
    tags = {}
    for fname, key in tag_fields:
        val = getattr(feat, fname, None)
        if val is not None and str(val).strip():
            tags[key] = str(val)
    return tags


def _parse_tags(element):
    """Extracts {k: v} pairs from <tag k="..." v="..."/> children."""
    return {tag.get("k"): tag.get("v") for tag in element.findall("tag")}


def _decode_layer_way_id(way_id):
    """Return (table_idx, fid, part_i) if way_id belongs to a layer table way."""
    if _LAYER_ID_BASE <= way_id < _VERTEX_BASE:
        ti = way_id // _LAYER_ID_BASE - 1
        rem = way_id % _LAYER_ID_BASE
        if 0 <= ti < len(_LAYER_MODELS):
            return ti, rem // 100, rem % 100
    return None


def _decode_layer_point_id(node_id):
    """Return (table_idx, fid, sub_i) if node_id belongs to a layer point feature."""
    if _LAYER_ID_BASE <= node_id < _VERTEX_BASE:
        ti = node_id // _LAYER_ID_BASE - 1
        rem = node_id % _LAYER_ID_BASE
        if 0 <= ti < len(_LAYER_MODELS) and _geom_kind(_LAYER_MODELS[ti]) == 'point':
            return ti, rem // 100, rem % 100
    return None


def _decode_vertex_id(node_id):
    """Return (table_idx, fid, part_i, v_i) if node_id is a synthetic vertex node."""
    if node_id >= _VERTEX_BASE:
        rem = node_id - _VERTEX_BASE
        ti = rem // _VTX_TABLE_STRIDE
        rem2 = rem % _VTX_TABLE_STRIDE
        fi = rem2 // _VTX_FEAT_STRIDE
        rem3 = rem2 % _VTX_FEAT_STRIDE
        pi = rem3 // _VTX_PART_STRIDE
        vi = rem3 % _VTX_PART_STRIDE
        if 0 <= ti < len(_LAYER_MODELS):
            return ti, fi, pi, vi
    return None


def _update_layer_tags(model, fid, new_tags):
    """Update layer table fields from an OSM tag dict. Returns new version."""
    rev_remap = {v: k for k, v in _REMAP.items()}
    model_fields = {f.name for f in model._meta.fields}
    try:
        feat = model.objects.get(fid=fid)
    except model.DoesNotExist:
        return 1
    for osm_key, value in new_tags.items():
        field = rev_remap.get(osm_key, osm_key)
        if field in model_fields and field not in _SKIP:
            setattr(feat, field, value or None)
    feat.version = (getattr(feat, 'version', 1) or 1) + 1
    feat.save()
    return feat.version


def _update_vertex_geom(table_idx, fid, part_i, v_i, new_lat, new_lon):
    """Replace one vertex coordinate in a line/polygon layer feature geometry."""
    from django.contrib.gis.geos import (
        MultiLineString, LineString, MultiPolygon, Polygon as GEOSPolygon,
    )
    model = _LAYER_MODELS[table_idx]
    kind = _geom_kind(model)
    try:
        feat = model.objects.get(fid=fid)
    except model.DoesNotExist:
        return
    if feat.geom is None or part_i >= feat.geom.num_geom:
        return

    if kind == 'line':
        parts = []
        for i in range(feat.geom.num_geom):
            coords = list(feat.geom[i].coords)
            if i == part_i and v_i < len(coords):
                coords[v_i] = (new_lon, new_lat)
            parts.append(LineString(coords, srid=4326))
        feat.geom = MultiLineString(parts, srid=4326)

    elif kind == 'polygon':
        polys = []
        for i in range(feat.geom.num_geom):
            ring = list(feat.geom[i].exterior_ring.coords)  # closed ring
            if i == part_i and v_i < len(ring) - 1:
                ring[v_i] = (new_lon, new_lat)
                ring[-1] = ring[0]  # keep closed
            polys.append(GEOSPolygon(ring, srid=4326))
        feat.geom = MultiPolygon(polys, srid=4326)

    feat.version = (getattr(feat, 'version', 1) or 1) + 1
    feat.save()


def escape_xml(value):
    """Escape characters that are illegal inside an XML attribute value."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_node_xml(node, tags_by_node):
    tags = tags_by_node.get(node.id, [])
    tag_lines = "".join(
        f'<tag k="{escape_xml(t.k)}" v="{escape_xml(t.v)}"/>' for t in tags
    )
    changeset_id = node.changeset_id or 0
    timestamp = node.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    if tag_lines:
        return (
            f'<node id="{node.id}" version="{node.version}" '
            f'changeset="{changeset_id}" timestamp="{timestamp}" '
            f'visible="{"true" if node.visible else "false"}" '
            f'lat="{node.lat}" lon="{node.lon}">{tag_lines}</node>'
        )
    return (
        f'<node id="{node.id}" version="{node.version}" '
        f'changeset="{changeset_id}" timestamp="{timestamp}" '
        f'visible="{"true" if node.visible else "false"}" '
        f'lat="{node.lat}" lon="{node.lon}"/>'
    )


def render_way_xml(way, node_refs_by_way, tags_by_way):
    nd_lines = "".join(f'<nd ref="{ref}"/>' for ref in node_refs_by_way.get(way.id, []))
    tags = tags_by_way.get(way.id, [])
    tag_lines = "".join(
        f'<tag k="{escape_xml(t.k)}" v="{escape_xml(t.v)}"/>' for t in tags
    )
    changeset_id = way.changeset_id or 0
    timestamp = way.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    return (
        f'<way id="{way.id}" version="{way.version}" '
        f'changeset="{changeset_id}" timestamp="{timestamp}" '
        f'visible="{"true" if way.visible else "false"}">'
        f"{nd_lines}{tag_lines}</way>"
    )


def _collect_map_elements(min_lon, min_lat, max_lon, max_lat):
    """
    Shared logic: query 46 layer tables + osm_nodes/osm_ways for the given
    bbox and return (node_list, way_list) as plain dicts suitable for both
    XML and JSON rendering.

    Each node dict: {id, version, lat, lon, timestamp, tags}
    Each way  dict: {id, version, nodes (list of node ids), timestamp, tags}
    """
    bbox_poly    = Polygon.from_bbox((min_lon, min_lat, max_lon, max_lat))
    request_area = (max_lon - min_lon) * (max_lat - min_lat)

    nodes = []
    ways  = []

    # ── layer tables ──────────────────────────────────────────────────
    for table_idx, model in enumerate(_LAYER_MODELS):
        if model._meta.db_table in _SKIP_EDITING:
            continue
        kind = _geom_kind(model)
        if kind is None:
            continue

        tag_fields    = _tag_fields(model)
        table_id_base = (table_idx + 1) * _LAYER_ID_BASE
        vtx_table_base = _VERTEX_BASE + table_idx * _VTX_TABLE_STRIDE

        try:
            features = list(model.objects.filter(geom__bboverlaps=bbox_poly))
        except Exception:
            continue

        for feat in features:
            if feat.geom is None:
                continue
            try:
                env = feat.geom.envelope
                feat_area = (env.extent[2] - env.extent[0]) * (env.extent[3] - env.extent[1])
                if feat_area > request_area * _MAX_FEATURE_BBOX_RATIO:
                    continue
            except Exception:
                pass

            fid      = feat.fid
            feat_ver = getattr(feat, 'version', 1) or 1
            feat_ts  = (getattr(feat, 'updated_at', None)
                        or getattr(feat, 'created_at', None)
                        or timezone.now())
            ts_str   = feat_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
            tags     = _feat_tags(feat, tag_fields)
            num_geom = feat.geom.num_geom

            if kind == 'point':
                for i in range(num_geom):
                    pt = feat.geom[i]
                    nodes.append({
                        'id': table_id_base + fid * 100 + i,
                        'version': feat_ver, 'lat': pt.y, 'lon': pt.x,
                        'timestamp': ts_str, 'tags': tags if i == 0 else {},
                    })
            else:
                for part_i in range(num_geom):
                    part = feat.geom[part_i]
                    way_id = table_id_base + fid * 100 + part_i

                    if kind == 'polygon':
                        unique = list(part.exterior_ring.coords)[:-1]
                    else:
                        unique = list(part.coords)
                    if len(unique) < 2:
                        continue

                    vtx_base = vtx_table_base + fid * _VTX_FEAT_STRIDE + part_i * _VTX_PART_STRIDE
                    nd_ids   = []
                    for v_i, coord in enumerate(unique):
                        vtx_id = vtx_base + v_i
                        nodes.append({
                            'id': vtx_id, 'version': 1,
                            'lat': coord[1], 'lon': coord[0],
                            'timestamp': ts_str, 'tags': {},
                        })
                        nd_ids.append(vtx_id)

                    if kind == 'polygon':
                        nd_ids.append(nd_ids[0])

                    ways.append({
                        'id': way_id, 'version': feat_ver,
                        'nodes': nd_ids, 'timestamp': ts_str, 'tags': tags,
                    })

    # ── user edits (osm_nodes / osm_ways) ────────────────────────────
    osm_nodes_in_bbox = list(OsmNode.objects.filter(visible=True, geom__within=bbox_poly))
    node_ids_in_bbox  = {n.id for n in osm_nodes_in_bbox}

    osm_way_ids = set(
        OsmWayNode.objects.filter(node_id__in=node_ids_in_bbox)
        .values_list('way_id', flat=True).distinct()
    )
    osm_ways = list(OsmWay.objects.filter(visible=True, id__in=osm_way_ids))

    osm_wn = list(
        OsmWayNode.objects.filter(way_id__in=osm_way_ids).order_by('way_id', 'sequence_id')
    )
    refs_by_way = {}
    for wn in osm_wn:
        refs_by_way.setdefault(wn.way_id, []).append(wn.node_id)

    extra_node_ids = {wn.node_id for wn in osm_wn} - node_ids_in_bbox
    extra_nodes    = list(OsmNode.objects.filter(id__in=extra_node_ids)) if extra_node_ids else []
    all_osm_nodes  = osm_nodes_in_bbox + extra_nodes

    ntags_qs   = OsmNodeTag.objects.filter(node_id__in=[n.id for n in all_osm_nodes])
    tags_by_node = {}
    for t in ntags_qs:
        tags_by_node.setdefault(t.node_id, {})[t.k] = t.v

    wtags_qs   = OsmWayTag.objects.filter(way_id__in=osm_way_ids)
    tags_by_way = {}
    for t in wtags_qs:
        tags_by_way.setdefault(t.way_id, {})[t.k] = t.v

    for n in all_osm_nodes:
        ts = n.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ') if n.timestamp else '2024-01-01T00:00:00Z'
        nodes.append({
            'id': n.id, 'version': n.version, 'lat': n.lat, 'lon': n.lon,
            'timestamp': ts, 'tags': tags_by_node.get(n.id, {}),
        })
    for w in osm_ways:
        ts = w.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ') if w.timestamp else '2024-01-01T00:00:00Z'
        ways.append({
            'id': w.id, 'version': w.version,
            'nodes': refs_by_way.get(w.id, []),
            'timestamp': ts, 'tags': tags_by_way.get(w.id, {}),
        })

    return nodes, ways
