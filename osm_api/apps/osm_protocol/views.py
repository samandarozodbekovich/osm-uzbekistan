from rest_framework.views import APIView
import gzip
from django.contrib.gis.geos import Polygon
from django.http import HttpResponse, HttpResponseBadRequest

from apps.id_editor.models import OsmNode, OsmWay, OsmWayNode

import xml.etree.ElementTree as ET

from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.web_app.models import OsmChangeset
from apps.id_editor.models import (
    OsmNode, OsmWay, OsmWayNode, OsmNodeTag, OsmWayTag,
)

from rest_framework.permissions import IsAuthenticated
from apps.web_app.models import OsmChangeset


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


class ChangesetUploadView(APIView):
    """
    POST /api/0.6/changeset/{id}/upload

    Accepts an osmChange XML document (<osmChange><create>...</create>
    <modify>...</modify><delete>...</delete></osmChange>) describing every
    edit made in this session, applies it, and returns a <diffResult>
    mapping the client's temporary negative ids to the real database ids
    that were assigned.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, changeset_id):
        try:
            changeset = OsmChangeset.objects.get(id=changeset_id, uid=request.user.id, open=True)
        except OsmChangeset.DoesNotExist:
            return HttpResponse("Changeset not found or closed", status=404)
        
        # iD (via osm-auth) compresses the upload body with gzip and sets
        # Content-Encoding: gzip. Django doesn't decompress this
        # automatically for raw request.body, so we do it ourselves.
        body = request.body
        content_encoding = request.META.get("HTTP_CONTENT_ENCODING", "")

        # --- TEMPORARY DEBUG: remove once upload works ---
        print(f"[upload debug] Content-Encoding header: {content_encoding!r}")
        print(f"[upload debug] raw body length: {len(body)}")
        print(f"[upload debug] first 20 bytes: {body[:20]!r}")
        # ---------------------------------------------------

        if content_encoding.lower() == "gzip":
            try:
                body = gzip.decompress(body)
            except OSError as e:
                print(f"[upload debug] gzip.decompress failed: {e}")
                return HttpResponseBadRequest("Invalid gzip payload")

        try:
            root = ET.fromstring(body)
        except ET.ParseError as e:
            print(f"[upload debug] XML parse failed: {e}")
            print(f"[upload debug] decoded body (first 500 chars): {body[:500]!r}")
            return HttpResponseBadRequest("Invalid XML")

        # Maps the client's temporary negative ids (e.g. -1, -2) to the
        # real database ids assigned during this upload, so that <way>
        # elements referencing newly-created nodes resolve correctly.
        id_map = {"node": {}, "way": {}, "relation": {}}
        diff_entries = []  # (type, old_id, new_id, new_version)

        with transaction.atomic():
            create_block = root.find("create")
            if create_block is not None:
                # Nodes first, since ways reference them.
                for node_el in create_block.findall("node"):
                    old_id = int(node_el.get("id"))
                    node = OsmNode.objects.create(
                        version=1,
                        visible=True,
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
                        real_node_id = id_map["node"].get(ref, ref)
                        OsmWayNode.objects.create(way=way, sequence_id=seq, node_id=real_node_id)
                    id_map["way"][old_id] = way.id
                    diff_entries.append(("way", old_id, way.id, way.version))

            modify_block = root.find("modify")
            if modify_block is not None:
                for node_el in modify_block.findall("node"):
                    node_id = int(node_el.get("id"))
                    node = OsmNode.objects.get(id=node_id)
                    node.lat = float(node_el.get("lat"))
                    node.lon = float(node_el.get("lon"))
                    node.version += 1
                    node.changeset = changeset
                    node.save()
                    OsmNodeTag.objects.filter(node=node).delete()
                    for k, v in _parse_tags(node_el).items():
                        OsmNodeTag.objects.create(node=node, k=k, v=v)
                    diff_entries.append(("node", node_id, node.id, node.version))

                for way_el in modify_block.findall("way"):
                    way_id = int(way_el.get("id"))
                    way = OsmWay.objects.get(id=way_id)
                    way.version += 1
                    way.changeset = changeset
                    way.save()
                    OsmWayTag.objects.filter(way=way).delete()
                    for k, v in _parse_tags(way_el).items():
                        OsmWayTag.objects.create(way=way, k=k, v=v)
                    OsmWayNode.objects.filter(way=way).delete()
                    for seq, nd_el in enumerate(way_el.findall("nd")):
                        ref = int(nd_el.get("ref"))
                        real_node_id = id_map["node"].get(ref, ref)
                        OsmWayNode.objects.create(way=way, sequence_id=seq, node_id=real_node_id)
                    diff_entries.append(("way", way_id, way.id, way.version))

            delete_block = root.find("delete")
            if delete_block is not None:
                for node_el in delete_block.findall("node"):
                    node_id = int(node_el.get("id"))
                    OsmNode.objects.filter(id=node_id).update(visible=False)
                    diff_entries.append(("node", node_id, node_id, None))
                for way_el in delete_block.findall("way"):
                    way_id = int(way_el.get("id"))
                    OsmWay.objects.filter(id=way_id).update(visible=False)
                    diff_entries.append(("way", way_id, way_id, None))

        # Build the <diffResult> the client needs to reconcile its
        # temporary ids with the real ones assigned above.
        parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<diffResult version="0.6" generator="custom-osm-backend">']
        for el_type, old_id, new_id, new_version in diff_entries:
            if new_version is not None:
                parts.append(f'<{el_type} old_id="{old_id}" new_id="{new_id}" new_version="{new_version}"/>')
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
    OSM API v0.6 /map endpoint. Given a bbox, returns:
    - every node inside the bbox
    - every way that references at least one of those nodes
    - every node referenced by those ways, even if outside the bbox
      (required so iD can render the full geometry of a way)
    Relations are intentionally left out for this first version.
    """
    authentication_classes = []
    def get(self, request):
        bbox_param = request.query_params.get("bbox")
        if not bbox_param:
            return HttpResponseBadRequest("Missing required 'bbox' parameter.")

        try:
            min_lon, min_lat, max_lon, max_lat = (float(v) for v in bbox_param.split(","))
        except ValueError:
            return HttpResponseBadRequest("Invalid 'bbox' parameter format.")

        bbox_polygon = Polygon.from_bbox((min_lon, min_lat, max_lon, max_lat))

        # Step 1: nodes physically inside the bbox.
        nodes_in_bbox = list(
            OsmNode.objects.filter(visible=True, geom__within=bbox_polygon)
        )
        node_ids_in_bbox = {n.id for n in nodes_in_bbox}

        # Step 2: ways that reference at least one of those nodes.
        way_ids = set(
            OsmWayNode.objects.filter(node_id__in=node_ids_in_bbox)
            .values_list("way_id", flat=True)
            .distinct()
        )
        ways = list(OsmWay.objects.filter(visible=True, id__in=way_ids))

        # Step 3: full ordered node list for each way (may include nodes
        # outside the bbox — those need to be fetched and output too).
        way_nodes = list(
            OsmWayNode.objects.filter(way_id__in=way_ids).order_by("way_id", "sequence_id")
        )
        node_refs_by_way = {}
        for wn in way_nodes:
            node_refs_by_way.setdefault(wn.way_id, []).append(wn.node_id)

        all_referenced_node_ids = {wn.node_id for wn in way_nodes}
        missing_node_ids = all_referenced_node_ids - node_ids_in_bbox
        extra_nodes = list(OsmNode.objects.filter(id__in=missing_node_ids)) if missing_node_ids else []

        all_nodes = nodes_in_bbox + extra_nodes

        # Step 4: tags for everything we're about to render.
        from apps.id_editor.models import OsmNodeTag, OsmWayTag

        node_tags = OsmNodeTag.objects.filter(node_id__in=[n.id for n in all_nodes])
        tags_by_node = {}
        for t in node_tags:
            tags_by_node.setdefault(t.node_id, []).append(t)

        way_tags = OsmWayTag.objects.filter(way_id__in=way_ids)
        tags_by_way = {}
        for t in way_tags:
            tags_by_way.setdefault(t.way_id, []).append(t)

        # Step 5: assemble the XML response.
        node_xml = "".join(render_node_xml(n, tags_by_node) for n in all_nodes)
        way_xml = "".join(render_way_xml(w, node_refs_by_way, tags_by_way) for w in ways)

        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<osm version="0.6" generator="custom-osm-backend">'
            f'<bounds minlat="{min_lat}" minlon="{min_lon}" '
            f'maxlat="{max_lat}" maxlon="{max_lon}"/>'
            f"{node_xml}{way_xml}"
            "</osm>"
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


class MapDataJsonView(APIView):
    """
    JSON variant of /map, requested by iD as map.json.
    Reuses the same query logic as MapDataView but returns a JSON
    structure matching OSM API's alternate JSON output format
    instead of XML.
    """
    authentication_classes = []
    def get(self, request):
        bbox_param = request.query_params.get("bbox")
        if not bbox_param:
            return HttpResponseBadRequest("Missing required 'bbox' parameter.")

        try:
            min_lon, min_lat, max_lon, max_lat = (float(v) for v in bbox_param.split(","))
        except ValueError:
            return HttpResponseBadRequest("Invalid 'bbox' parameter format.")

        bbox_polygon = Polygon.from_bbox((min_lon, min_lat, max_lon, max_lat))

        nodes_in_bbox = list(OsmNode.objects.filter(visible=True, geom__within=bbox_polygon))
        node_ids_in_bbox = {n.id for n in nodes_in_bbox}

        way_ids = set(
            OsmWayNode.objects.filter(node_id__in=node_ids_in_bbox)
            .values_list("way_id", flat=True)
            .distinct()
        )
        ways = list(OsmWay.objects.filter(visible=True, id__in=way_ids))

        way_nodes = list(
            OsmWayNode.objects.filter(way_id__in=way_ids).order_by("way_id", "sequence_id")
        )
        node_refs_by_way = {}
        for wn in way_nodes:
            node_refs_by_way.setdefault(wn.way_id, []).append(wn.node_id)

        all_referenced_node_ids = {wn.node_id for wn in way_nodes}
        missing_node_ids = all_referenced_node_ids - node_ids_in_bbox
        extra_nodes = list(OsmNode.objects.filter(id__in=missing_node_ids)) if missing_node_ids else []
        all_nodes = nodes_in_bbox + extra_nodes

        from apps.id_editor.models import OsmNodeTag, OsmWayTag

        node_tags = OsmNodeTag.objects.filter(node_id__in=[n.id for n in all_nodes])
        tags_by_node = {}
        for t in node_tags:
            tags_by_node.setdefault(t.node_id, {})[t.k] = t.v

        way_tags = OsmWayTag.objects.filter(way_id__in=way_ids)
        tags_by_way = {}
        for t in way_tags:
            tags_by_way.setdefault(t.way_id, {})[t.k] = t.v

        elements = []
        for n in all_nodes:
            elements.append({
                "type": "node",
                "id": n.id,
                "version": n.version,
                "changeset": n.changeset_id or 0,
                "timestamp": n.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "visible": n.visible,
                "lat": n.lat,
                "lon": n.lon,
                "tags": tags_by_node.get(n.id, {}),
            })
        for w in ways:
            elements.append({
                "type": "way",
                "id": w.id,
                "version": w.version,
                "changeset": w.changeset_id or 0,
                "timestamp": w.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "visible": w.visible,
                "nodes": node_refs_by_way.get(w.id, []),
                "tags": tags_by_way.get(w.id, {}),
            })

        return Response({
            "version": "0.6",
            "generator": "custom-osm-backend",
            "bounds": {
                "minlat": min_lat, "minlon": min_lon,
                "maxlat": max_lat, "maxlon": max_lon,
            },
            "elements": elements,
        })