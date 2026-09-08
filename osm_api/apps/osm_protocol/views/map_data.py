from django.contrib.gis.geos import Polygon
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.views import APIView

from .helpers import escape_xml, _collect_map_elements


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
