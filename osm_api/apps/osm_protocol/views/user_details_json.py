from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
