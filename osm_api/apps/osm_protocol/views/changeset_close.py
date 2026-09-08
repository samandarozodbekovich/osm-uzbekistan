from django.http import HttpResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.web_app.models import OsmChangeset


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
