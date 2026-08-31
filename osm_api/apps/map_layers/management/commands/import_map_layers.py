"""
apps/map_layers/management/commands/import_map_layers.py

Imports each source layer (shp dir or gpkg) into ITS OWN generated model,
looked up via LAYER_MODEL_MAP (built by generate_layer_models). Field
values are mapped straight onto real typed model fields - no JSONField.

Usage:
    python manage.py import_map_layers "C:\\...\\map_work\\data"
    python manage.py import_map_layers "C:\\...\\map_work\\data.gpkg" --replace
"""

import os

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.map_layers.models import LAYER_MODEL_MAP

BATCH_SIZE = 2000


class Command(BaseCommand):
    help = "Import shapefile/gpkg layers into their matching generated models (LAYER_MODEL_MAP)."

    def add_arguments(self, parser):
        parser.add_argument("path", type=str)
        parser.add_argument("--source", type=str, default="nextgis")
        parser.add_argument("--replace", action="store_true")

    def handle(self, *args, **options):
        path = options["path"]
        self.source = options["source"]
        self.replace = options["replace"]

        if path.lower().endswith(".gpkg"):
            for layer in DataSource(path):
                self._import_layer(layer, layer.name)
        elif os.path.isdir(path):
            shp_files = sorted(f for f in os.listdir(path) if f.lower().endswith(".shp"))
            if not shp_files:
                raise CommandError(f"No .shp files found in {path}")
            for fname in shp_files:
                layer_name = os.path.splitext(fname)[0]
                ds = DataSource(os.path.join(path, fname))
                self._import_layer(ds[0], layer_name)
        else:
            raise CommandError("Path must be a .gpkg file or a directory of .shp files")

    def _import_layer(self, layer, layer_name):
        model = LAYER_MODEL_MAP.get(layer_name)
        if model is None:
            self.stderr.write(
                f"Skipping '{layer_name}': no matching model in LAYER_MODEL_MAP. "
                f"Did you run generate_layer_models on the current schema?"
            )
            return

        self.stdout.write(f"Layer '{layer_name}' -> {model.__name__} ({len(layer)} features)")

        if self.replace:
            deleted, _ = model.objects.all().delete()
            if deleted:
                self.stdout.write(f"  removed {deleted} existing rows")

        field_names = list(layer.fields)
        model_field_names = {f.name for f in model._meta.fields}
        buffer = []
        imported = 0

        for feature in layer:
            geom = feature.geom
            if geom is None:
                continue
            if layer.srs and layer.srs.srid and layer.srs.srid != 4326:
                geom.transform(4326)

            try:
                geos_geom = GEOSGeometry(geom.wkt, srid=4326)
            except Exception as exc:
                self.stderr.write(f"  skipping feature with invalid geometry: {exc}")
                continue

            kwargs = {"geom": geos_geom, "source": self.source}
            for raw_name in field_names:
                field_name = self._sanitized(raw_name)
                if field_name in model_field_names:
                    try:
                        kwargs[field_name] = feature.get(raw_name)
                    except Exception:
                        kwargs[field_name] = None

            buffer.append(model(**kwargs))

            if len(buffer) >= BATCH_SIZE:
                self._flush(model, buffer)
                imported += len(buffer)
                self.stdout.write(f"  ... {imported} imported")
                buffer = []

        if buffer:
            self._flush(model, buffer)
            imported += len(buffer)

        self.stdout.write(self.style.SUCCESS(f"  done: {imported} features"))

    @staticmethod
    def _flush(model, buffer):
        with transaction.atomic():
            model.objects.bulk_create(buffer, batch_size=BATCH_SIZE)

    @staticmethod
    def _sanitized(raw_name):
        # Must mirror generate_layer_models._field_name() exactly, or field
        # values won't line up with the generated model's attributes.
        import re
        name = raw_name.strip().lower()
        name = re.sub(r"[^0-9a-z_]", "_", name)
        if not name or name[0].isdigit():
            name = f"f_{name}"
        if name in ("id", "geom", "source", "version", "needs_review",
                     "created_at", "updated_at", "updated_by"):
            name = f"attr_{name}"
        return name