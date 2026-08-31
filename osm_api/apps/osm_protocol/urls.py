from django.urls import path
from .views import (
    CapabilitiesView, MapDataView, CapabilitiesJsonView, MapDataJsonView,
    ChangesetCreateView, ChangesetCloseView, ChangesetUploadView, UserDetailsJsonView,
)

urlpatterns = [
    path("capabilities", CapabilitiesView.as_view(), name="osm-capabilities"),
    path("0.6/capabilities", CapabilitiesView.as_view(), name="osm-capabilities-v6"),
    path("capabilities.json", CapabilitiesJsonView.as_view(), name="osm-capabilities-json"),
    path("0.6/capabilities.json", CapabilitiesJsonView.as_view(), name="osm-capabilities-v6-json"),

    path("0.6/map", MapDataView.as_view(), name="osm-map"),
    path("0.6/map.json", MapDataJsonView.as_view(), name="osm-map-json"),

    path("0.6/changeset/create", ChangesetCreateView.as_view(), name="osm-changeset-create"),
    path("0.6/changeset/<int:changeset_id>/close", ChangesetCloseView.as_view(), name="osm-changeset-close"),
    path("0.6/changeset/<int:changeset_id>/upload", ChangesetUploadView.as_view(), name="osm-changeset-upload"),
    path("0.6/user/details.json", UserDetailsJsonView.as_view(), name="osm-user-details-json"),
]