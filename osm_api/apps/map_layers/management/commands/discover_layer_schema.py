"""
apps/map_layers/management/commands/discover_layer_schema.py

Handles THREE possible input shapes:
    1. A single multi-layer .gpkg file (rare)
    2. A directory of .shp files (one layer per file)
    3. A directory of single-layer .gpkg files (your NextGIS export:
       building-polygon.gpkg, highway-line.gpkg, etc. - one file per layer)

The canonical layer name is always the FILE'S BASENAME (not GDAL's internal
layer name inside the file), since that's what's unique and descriptive
here (e.g. "building-polygon", "highway-line"). generate_layer_models and
import_map_layers both key off this same name.

Usage:
    python manage.py discover_layer_schema "C:\\...\\map_work\\data" --out layer_schema.json
"""

import json
import os

from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand, CommandError

GDAL_TO_DJANGO_TYPE = {
    "OFTInteger": "integer",
    "OFTInteger64": "integer",
    "OFTReal": "float",
    "OFTString": "string",
    "OFTDate": "date",
    "OFTDateTime": "datetime",
    "OFTTime": "time",
}


class Command(BaseCommand):
    help = "Discover field schema for every layer (one file per layer, or multi-layer gpkg), write to JSON."

    def add_arguments(self, parser):
        parser.add_argument("path", type=str)
        parser.add_argument("--out", type=str, default="layer_schema.json")

    def handle(self, *args, **options):
        path = options["path"]
        out_path = options["out"]

        # (canonical_name, layer_object) pairs
        named_layers = []

        if os.path.isdir(path):
            data_files = sorted(
                f for f in os.listdir(path)
                if f.lower().endswith((".shp", ".gpkg"))
            )
            if not data_files:
                raise CommandError(f"No .shp or .gpkg files found in {path}")

            for fname in data_files:
                basename = os.path.splitext(fname)[0]
                ds = DataSource(os.path.join(path, fname))
                if len(ds) == 1:
                    named_layers.append((basename, ds[0]))
                else:
                    # rare: a single file containing multiple layers
                    for layer in ds:
                        named_layers.append((f"{basename}__{layer.name}", layer))

        elif path.lower().endswith(".gpkg"):
            ds = DataSource(path)
            for layer in ds:
                named_layers.append((layer.name, layer))
        else:
            raise CommandError("Path must be a directory or a .gpkg file")

        if not named_layers:
            raise CommandError("No layers found")

        schema = {}
        for layer_name, layer in named_layers:
            field_defs = []
            for name, ftype in zip(layer.fields, layer.field_types):
                type_name = ftype.__name__ if hasattr(ftype, "__name__") else str(ftype)
                field_defs.append({
                    "name": name,
                    "gdal_type": type_name,
                    "django_type": GDAL_TO_DJANGO_TYPE.get(type_name, "string"),
                })

            schema[layer_name] = {
                "geom_type": layer.geom_type.name if layer.geom_type else "Unknown",
                "srid": layer.srs.srid if layer.srs else None,
                "feature_count": len(layer),
                "fields": field_defs,
            }

            self.stdout.write(
                f"{layer_name}: {len(layer)} features, {len(field_defs)} fields, "
                f"geom={layer.geom_type.name if layer.geom_type else '?'}"
            )

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"\nSchema for {len(schema)} layers written to {out_path}"))