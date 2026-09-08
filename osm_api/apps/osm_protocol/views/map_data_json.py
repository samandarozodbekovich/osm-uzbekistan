from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import _collect_map_elements


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
