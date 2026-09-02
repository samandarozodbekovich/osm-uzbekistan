import gzip
import inspect

import xml.etree.ElementTree as ET

from django.contrib.gis.db.models import (
    MultiPointField, MultiLineStringField, MultiPolygonField,
    PointField, LineStringField, PolygonField,
)
from django.contrib.gis.geos import Polygon
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.web_app.models import OsmChangeset
from apps.id_editor.models import (
    OsmNode, OsmWay, OsmWayNode, OsmNodeTag, OsmWayTag,
)
import apps.map_layers.models as _layer_models

# ── ID namespacing ────────────────────────────────────────────────────────────
# Point/way IDs: (table_idx + 1) * 10^9 + fid*100 + sub_geom_idx
#   max ≈ 46 * 1B + 1M*100 = 46B + 100M ≈ 46B
# Vertex node IDs: VERTEX_BASE + table_idx*200B + fid*100K + part_i*10K + vertex_seq
#   max ≈ 10T + 46*200B + 1M*100K = 10T + 9.2T + 100B ≈ 19.3T
# User-edit IDs (osm_nodes/osm_ways): regular small DB ids (< 1B)
# All ranges: user-edits < 1B << layer IDs ~46B << vertex IDs ~10T << JS safe int ~9e15
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


class UserDetailsJsonView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "version": "0.6",
            "generator": "custom-osm-backend",
            "user": {
                "id": user.id,
                "display_name": getattr(user, "phone_number", str(user)),
                "account_created": user.date_joined.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "changesets": {
                    "count": OsmChangeset.objects.filter(uid=user.id).count()
                },
            }
        })


def _parse_tags(element):
    """Extracts {k: v} pairs from <tag k="..." v="..."/> children."""
    return {tag.get("k"): tag.get("v") for tag in element.findall("tag")}


class ChangesetCreateView(APIView):
    """
    PUT /api/0.6/changeset/create

    Creates a new open changeset for the authenticated user and returns
    its id as plain text — this is the real OSM API's response format
    for this endpoint (not XML, not JSON).
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        changeset = OsmChangeset.objects.create(
            user=getattr(request.user, "phone_number", str(request.user)),
            uid=request.user.id,
        )
        return HttpResponse(str(changeset.id), content_type="text/plain")


class ChangesetCloseView(APIView):
    """PUT /api/0.6/changeset/{id}/close"""
    permission_classes = [IsAuthenticated]

    def put(self, request, changeset_id):
        try:
            changeset = OsmChangeset.objects.get(id=changeset_id, uid=request.user.id)
        except OsmChangeset.DoesNotExist:
            return HttpResponse("Changeset not found", status=404)

        changeset.open = False
        changeset.closed_at = timezone.now()
        changeset.save(update_fields=["open", "closed_at"])
        return HttpResponse(status=200)


# ── Changeset upload helpers ──────────────────────────────────────────────────

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


class ChangesetUploadView(APIView):
    """
    POST /api/0.6/changeset/{id}/upload

    Accepts osmChange XML and applies it. Layer table features (ways/nodes
    with IDs in the layer-table range) are updated in their source tables.
    Newly created features are stored in osm_nodes / osm_ways as before.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, changeset_id):
        try:
            changeset = OsmChangeset.objects.get(id=changeset_id, uid=request.user.id, open=True)
        except OsmChangeset.DoesNotExist:
            return HttpResponse("Changeset not found or closed", status=404)

        body = request.body
        if request.META.get("HTTP_CONTENT_ENCODING", "").lower() == "gzip":
            try:
                body = gzip.decompress(body)
            except OSError:
                return HttpResponseBadRequest("Invalid gzip payload")

        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            return HttpResponseBadRequest("Invalid XML")

        id_map = {"node": {}, "way": {}}
        diff_entries = []
        # synthetic vertex/layer node IDs → real osm_node IDs created on-the-fly
        _syn_node_map: dict = {}

        def _real_nd(ref: int):
            """
            Resolve an <nd ref> to a real osm_nodes ID.
            Synthetic IDs (layer table IDs or vertex IDs) are looked up in the
            layer table and a throw-away OsmNode is created so FK constraints
            on osm_way_nodes remain satisfied.  Returns None to skip the nd.
            """
            real = id_map["node"].get(ref, ref)
            if real < _LAYER_ID_BASE:
                return real
            if real in _syn_node_map:
                return _syn_node_map[real]

            lat, lon = None, None
            vtx = _decode_vertex_id(real)
            if vtx:
                ti, fi, pi, vi = vtx
                model = _LAYER_MODELS[ti]
                kind = _geom_kind(model)
                try:
                    feat = model.objects.get(fid=fi)
                    if feat.geom and pi < feat.geom.num_geom:
                        if kind == 'line':
                            coords = list(feat.geom[pi].coords)
                            if vi < len(coords):
                                lon, lat = coords[vi][0], coords[vi][1]
                        elif kind == 'polygon':
                            ring = list(feat.geom[pi].exterior_ring.coords)
                            if vi < len(ring):
                                lon, lat = ring[vi][0], ring[vi][1]
                except Exception:
                    pass
            else:
                pt = _decode_layer_point_id(real)
                if pt:
                    ti, fi, si = pt
                    model = _LAYER_MODELS[ti]
                    try:
                        feat = model.objects.get(fid=fi)
                        if feat.geom and si < feat.geom.num_geom:
                            g = feat.geom[si]
                            lon, lat = float(g.x), float(g.y)
                    except Exception:
                        pass

            if lat is not None and lon is not None:
                rn = OsmNode.objects.create(version=1, visible=True, lat=lat, lon=lon)
                _syn_node_map[real] = rn.id
                id_map["node"][ref] = rn.id
                return rn.id
            _syn_node_map[real] = None
            return None

        with transaction.atomic():

            # ── CREATE ────────────────────────────────────────────────
            create_block = root.find("create")
            if create_block is not None:
                for node_el in create_block.findall("node"):
                    old_id = int(node_el.get("id"))
                    node = OsmNode.objects.create(
                        version=1, visible=True,
                        lat=float(node_el.get("lat")),
                        lon=float(node_el.get("lon")),
                        changeset=changeset,
                    )
                    for k, v in _parse_tags(node_el).items():
                        OsmNodeTag.objects.create(node=node, k=k, v=v)
                    id_map["node"][old_id] = node.id
                    diff_entries.append(("node", old_id, node.id, node.version))

                for way_el in create_block.findall("way"):
                    old_id = int(way_el.get("id"))
                    way = OsmWay.objects.create(version=1, visible=True, changeset=changeset)
                    for k, v in _parse_tags(way_el).items():
                        OsmWayTag.objects.create(way=way, k=k, v=v)
                    for seq, nd_el in enumerate(way_el.findall("nd")):
                        ref = int(nd_el.get("ref"))
                        real_id = _real_nd(ref)
                        if real_id is not None:
                            OsmWayNode.objects.create(way=way, sequence_id=seq, node_id=real_id)
                    id_map["way"][old_id] = way.id
                    diff_entries.append(("way", old_id, way.id, way.version))

            # ── MODIFY ────────────────────────────────────────────────
            modify_block = root.find("modify")
            if modify_block is not None:
                for node_el in modify_block.findall("node"):
                    node_id = int(node_el.get("id"))
                    new_lat  = float(node_el.get("lat"))
                    new_lon  = float(node_el.get("lon"))
                    new_tags = _parse_tags(node_el)

                    vtx = _decode_vertex_id(node_id)
                    if vtx:
                        ti, fi, pi, vi = vtx
                        _update_vertex_geom(ti, fi, pi, vi, new_lat, new_lon)
                        diff_entries.append(("node", node_id, node_id, 2))
                    elif _decode_layer_point_id(node_id):
                        # Point feature position change — update tags at minimum
                        ti, fi, _ = _decode_layer_point_id(node_id)
                        _update_layer_tags(_LAYER_MODELS[ti], fi, new_tags)
                        diff_entries.append(("node", node_id, node_id, 2))
                    else:
                        try:
                            node = OsmNode.objects.get(id=node_id)
                            node.lat, node.lon = new_lat, new_lon
                            node.version += 1
                            node.changeset = changeset
                            node.save()
                            OsmNodeTag.objects.filter(node=node).delete()
                            for k, v in new_tags.items():
                                OsmNodeTag.objects.create(node=node, k=k, v=v)
                            diff_entries.append(("node", node_id, node.id, node.version))
                        except OsmNode.DoesNotExist:
                            diff_entries.append(("node", node_id, node_id, 2))

                for way_el in modify_block.findall("way"):
                    way_id   = int(way_el.get("id"))
                    new_tags = _parse_tags(way_el)

                    layer = _decode_layer_way_id(way_id)
                    if layer:
                        ti, fi, _ = layer
                        new_ver = _update_layer_tags(_LAYER_MODELS[ti], fi, new_tags)
                        diff_entries.append(("way", way_id, way_id, new_ver))
                    else:
                        try:
                            way = OsmWay.objects.get(id=way_id)
                            way.version += 1
                            way.changeset = changeset
                            way.save()
                            OsmWayTag.objects.filter(way=way).delete()
                            for k, v in new_tags.items():
                                OsmWayTag.objects.create(way=way, k=k, v=v)
                            OsmWayNode.objects.filter(way=way).delete()
                            for seq, nd_el in enumerate(way_el.findall("nd")):
                                ref = int(nd_el.get("ref"))
                                real_id = _real_nd(ref)
                                if real_id is not None:
                                    OsmWayNode.objects.create(way=way, sequence_id=seq, node_id=real_id)
                            diff_entries.append(("way", way_id, way.id, way.version))
                        except OsmWay.DoesNotExist:
                            diff_entries.append(("way", way_id, way_id, 2))

            # ── DELETE ────────────────────────────────────────────────
            delete_block = root.find("delete")
            if delete_block is not None:
                for node_el in delete_block.findall("node"):
                    node_id = int(node_el.get("id"))
                    if not _decode_vertex_id(node_id) and not _decode_layer_point_id(node_id):
                        OsmNode.objects.filter(id=node_id).update(visible=False)
                    diff_entries.append(("node", node_id, node_id, None))
                for way_el in delete_block.findall("way"):
                    way_id = int(way_el.get("id"))
                    if not _decode_layer_way_id(way_id):
                        OsmWay.objects.filter(id=way_id).update(visible=False)
                    diff_entries.append(("way", way_id, way_id, None))

        parts = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<diffResult version="0.6" generator="custom-osm-backend">']
        for el_type, old_id, new_id, new_ver in diff_entries:
            if new_ver is not None:
                parts.append(f'<{el_type} old_id="{old_id}" new_id="{new_id}" new_version="{new_ver}"/>')
            else:
                parts.append(f'<{el_type} old_id="{old_id}"/>')
        parts.append("</diffResult>")
        return HttpResponse("".join(parts), content_type="text/xml; charset=utf-8")


class CapabilitiesView(APIView):
    authentication_classes = []
    """
    Tells the iD editor (and any OSM API client) what this server supports:
    version range, max area/nodes per request, changeset limits, etc.
    iD calls this once on startup before doing anything else.
    """

    def get(self, request):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="custom-osm-backend">
  <api>
    <version minimum="0.6" maximum="0.6"/>
    <area maximum="0.25"/>
    <note_area maximum="25"/>
    <tracepoints per_page="5000"/>
    <waynodes maximum="2000"/>
    <relationmembers maximum="32000"/>
    <changesets maximum_elements="10000"/>
    <timeout seconds="300"/>
    <status database="online" api="online" gpx="online"/>
  </api>
  <policy>
    <imagery>
      <blacklist regex=".*\\.example\\.com/.*"/>
    </imagery>
  </policy>
</osm>"""
        return HttpResponse(xml, content_type="text/xml; charset=utf-8")


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


class MapDataView(APIView):
    """
    OSM API v0.6 /map endpoint.

    Reads directly from the 46 PostGIS layer tables (no copying required).
    Point features  → <node> elements.
    Line features   → <way> with synthetic vertex <node> elements.
    Polygon features→ closed <way> with synthetic vertex <node> elements.

    User-created edits (osm_nodes / osm_ways) are also returned so that
    features saved via ChangesetUploadView remain visible.
    """
    authentication_classes = []

    # OSM API spec: refuse requests larger than this to protect the server.
    MAX_BBOX_AREA = 0.25  # square degrees

    def get(self, request):
        bbox_param = request.query_params.get("bbox")
        if not bbox_param:
            return HttpResponseBadRequest("Missing required 'bbox' parameter.")

        try:
            min_lon, min_lat, max_lon, max_lat = (float(v) for v in bbox_param.split(","))
        except ValueError:
            return HttpResponseBadRequest("Invalid 'bbox' parameter format.")

        area = (max_lon - min_lon) * (max_lat - min_lat)
        if area > self.MAX_BBOX_AREA:
            return HttpResponse(
                "The area you have requested is too large. "
                f"Requested: {area:.4f} sq-deg, limit: {self.MAX_BBOX_AREA}.",
                status=400,
                content_type="text/plain",
            )

        bbox_poly = Polygon.from_bbox((min_lon, min_lat, max_lon, max_lat))

        node_parts = []   # <node .../> XML strings
        way_parts  = []   # <way ...>...</way> XML strings

        nodes, ways = _collect_map_elements(min_lon, min_lat, max_lon, max_lat)

        # ── Render XML ────────────────────────────────────────────────
        node_parts = []
        way_parts  = []

        for n in nodes:
            tag_xml = ''.join(
                f'<tag k="{escape_xml(k)}" v="{escape_xml(v)}"/>'
                for k, v in n['tags'].items()
            )
            base = (
                f'<node id="{n["id"]}" version="{n["version"]}" '
                f'changeset="0" timestamp="{n["timestamp"]}" visible="true" '
                f'lat="{n["lat"]}" lon="{n["lon"]}">'
            )
            if tag_xml:
                node_parts.append(base + tag_xml + '</node>')
            else:
                node_parts.append(base[:-1] + '/>')

        for w in ways:
            nd_xml  = ''.join(f'<nd ref="{r}"/>' for r in w['nodes'])
            tag_xml = ''.join(
                f'<tag k="{escape_xml(k)}" v="{escape_xml(v)}"/>'
                for k, v in w['tags'].items()
            )
            way_parts.append(
                f'<way id="{w["id"]}" version="{w["version"]}" '
                f'changeset="0" timestamp="{w["timestamp"]}" visible="true">'
                f'{nd_xml}{tag_xml}</way>'
            )

        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<osm version="0.6" generator="custom-osm-backend">'
            f'<bounds minlat="{min_lat}" minlon="{min_lon}" '
            f'maxlat="{max_lat}" maxlon="{max_lon}"/>'
            + ''.join(node_parts)
            + ''.join(way_parts)
            + '</osm>'
        )
        return HttpResponse(xml, content_type="text/xml; charset=utf-8")
    
from rest_framework.response import Response


class CapabilitiesJsonView(APIView):
    """
    JSON variant of /capabilities, requested by iD as capabilities.json.
    Must match the real OSM API's nested structure exactly — iD reads
    fields like data.api.version.minimum, not data.version.minimum.
    """
    authentication_classes = []
    def get(self, request):
        return Response({
            "version": "0.6",
            "generator": "custom-osm-backend",
            "copyright": "OpenStreetMap and contributors",
            "attribution": "http://www.openstreetmap.org/copyright",
            "license": "http://opendatacommons.org/licenses/odbl/1-0/",
            "api": {
                "version": {"minimum": "0.6", "maximum": "0.6"},
                "area": {"maximum": 0.25},
                "note_area": {"maximum": 25},
                "tracepoints": {"per_page": 5000},
                "waynodes": {"maximum": 2000},
                "relationmembers": {"maximum": 32000},
                "changesets": {
                    "maximum_elements": 10000,
                    "default_query_limit": 100,
                    "maximum_query_limit": 100,
                },
                "notes": {
                    "default_query_limit": 100,
                    "maximum_query_limit": 10000,
                },
                "timeout": {"seconds": 300},
                "status": {"database": "online", "api": "online", "gpx": "online"},
            },
            "policy": {
                "imagery": {
                    "blacklist": [{"regex": r".*\.example\.com/.*"}],
                },
            },
        })


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


class MapDataJsonView(APIView):
    """
    JSON variant of /map — called by iD editor as map.json.
    Returns the same data as MapDataView but in OSM JSON format.
    """
    authentication_classes = []
    MAX_BBOX_AREA = 0.25

    def get(self, request):
        bbox_param = request.query_params.get('bbox')
        if not bbox_param:
            return HttpResponseBadRequest("Missing required 'bbox' parameter.")
        try:
            min_lon, min_lat, max_lon, max_lat = (float(v) for v in bbox_param.split(','))
        except ValueError:
            return HttpResponseBadRequest("Invalid 'bbox' parameter format.")

        if (max_lon - min_lon) * (max_lat - min_lat) > self.MAX_BBOX_AREA:
            return HttpResponse("The area you have requested is too large.", status=400)

        nodes, ways = _collect_map_elements(min_lon, min_lat, max_lon, max_lat)

        elements = []
        for n in nodes:
            e = {
                'type': 'node', 'id': n['id'],
                'version': n['version'], 'changeset': 0,
                'timestamp': n['timestamp'], 'visible': True,
                'lat': n['lat'], 'lon': n['lon'],
            }
            if n['tags']:
                e['tags'] = n['tags']
            elements.append(e)

        for w in ways:
            e = {
                'type': 'way', 'id': w['id'],
                'version': w['version'], 'changeset': 0,
                'timestamp': w['timestamp'], 'visible': True,
                'nodes': w['nodes'],
            }
            if w['tags']:
                e['tags'] = w['tags']
            elements.append(e)

        return Response({
            'version': '0.6',
            'generator': 'custom-osm-backend',
            'bounds': {
                'minlat': min_lat, 'minlon': min_lon,
                'maxlat': max_lat, 'maxlon': max_lon,
            },
            'elements': elements,
        })