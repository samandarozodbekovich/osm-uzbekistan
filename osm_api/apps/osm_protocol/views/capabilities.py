from django.http import HttpResponse
from rest_framework.views import APIView


class CapabilitiesView(APIView):
    """
    Tells the iD editor (and any OSM API client) what this server supports:
    version range, max area/nodes per request, changeset limits, etc.
    iD calls this once on startup before doing anything else.
    """
    authentication_classes = []

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
