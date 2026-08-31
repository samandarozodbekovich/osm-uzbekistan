"""
apps/map_layers/api.py

Generic CRUD factory - discovers every concrete (non-abstract) subclass of
TrackingMixin in models.py and auto-builds a GeoJSON serializer + a
ModelViewSet + a router registration for it.

Add to your root urls.py:
    path("api/map-layers/", include("apps.map_layers.api")),

Requires: pip install djangorestframework-gis django-filter
"""

import inspect

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.routers import DefaultRouter
from rest_framework_gis.filters import InBBoxFilter
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from . import models as layer_models

router = DefaultRouter()


def _editable_field_names(model):
    return [f.name for f in model._meta.fields if f.name != model._meta.pk.name]


def _build_serializer(model):
    meta_attrs = {
        "model": model,
        "geo_field": "geom",
        "fields": _editable_field_names(model),
        "read_only_fields": ["edit_source", "version", "updated_at", "updated_by"],
    }
    meta_class = type("Meta", (), meta_attrs)
    return type(f"{model.__name__}Serializer", (GeoFeatureModelSerializer,), {"Meta": meta_class})


def _build_viewset(model):
    serializer_class = _build_serializer(model)

    class GeneratedViewSet(viewsets.ModelViewSet):
        queryset = model.objects.all()
        permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        filter_backends = [DjangoFilterBackend, InBBoxFilter]
        bbox_filter_field = "geom"
        filterset_fields = {"needs_review": ["exact"]}

        def perform_update(self, serializer):
            serializer.save(
                updated_by=self.request.user,
                version=serializer.instance.version + 1,
                edit_source="user_edit",
            )

    GeneratedViewSet.serializer_class = serializer_class
    GeneratedViewSet.__name__ = f"{model.__name__}ViewSet"
    return GeneratedViewSet


def _is_concrete_layer_model(obj):
    return (
        inspect.isclass(obj)
        and issubclass(obj, layer_models.TrackingMixin)
        and obj is not layer_models.TrackingMixin
        and not obj._meta.abstract
        and obj._meta.app_label == "map_layers"
    )


for _, model in inspect.getmembers(layer_models, _is_concrete_layer_model):
    slug = model.__name__.lower()
    router.register(slug, _build_viewset(model), basename=slug)

urlpatterns = router.urls