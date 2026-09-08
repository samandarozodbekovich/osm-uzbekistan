import gzip
import xml.etree.ElementTree as ET

from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.web_app.models import OsmChangeset
from apps.id_editor.models import (
    OsmNode, OsmWay, OsmWayNode, OsmNodeTag, OsmWayTag,
)

from .helpers import (
    _LAYER_ID_BASE, _LAYER_MODELS, _geom_kind, _parse_tags,
    _decode_layer_way_id, _decode_layer_point_id, _decode_vertex_id,
    _update_layer_tags, _update_vertex_geom,
)


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
