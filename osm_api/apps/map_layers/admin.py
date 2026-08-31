"""
apps/map_layers/admin.py
"""

import inspect

from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from . import models as layer_models


def _is_concrete_layer_model(obj):
    return (
        inspect.isclass(obj)
        and issubclass(obj, layer_models.TrackingMixin)
        and obj is not layer_models.TrackingMixin
        and not obj._meta.abstract
        and obj._meta.app_label == "map_layers"
    )


def _list_display_for(model):
    tracking = {"edit_source", "version", "needs_review", "created_at", "updated_at", "updated_by"}
    pk_name = model._meta.pk.name
    own_fields = [
        f.name for f in model._meta.fields
        if f.name not in tracking and f.name != pk_name
    ][:3]
    return [pk_name, *own_fields, "needs_review", "version", "updated_at"]


for _, model in inspect.getmembers(layer_models, _is_concrete_layer_model):
    admin_class = type(
        f"{model.__name__}Admin",
        (GISModelAdmin,),
        {
            "list_display": _list_display_for(model),
            "list_filter": ["needs_review"],
            "readonly_fields": ["edit_source", "version", "created_at", "updated_at", "updated_by"],
        },
    )
    admin.site.register(model, admin_class)