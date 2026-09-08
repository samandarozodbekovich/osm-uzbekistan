from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.web_app.models import OsmChangeset


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
