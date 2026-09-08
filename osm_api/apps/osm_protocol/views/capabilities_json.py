from rest_framework.response import Response
from rest_framework.views import APIView


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
