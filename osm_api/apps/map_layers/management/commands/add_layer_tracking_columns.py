"""
Adds the shared editing/tracking columns to every raw NextGIS table that
was just loaded via psql. Safe to re-run (uses ADD COLUMN IF NOT EXISTS).

Usage:
    python manage.py add_layer_tracking_columns
"""

from django.core.management.base import BaseCommand
from django.db import connection

# Exact table names created by the NextGIS .sql dumps (hyphens -> underscores).
TABLE_NAMES = [
    "aerialway_line", "aerialway_point", "airport_line", "airport_polygon",
    "boundary_polygon", "boundary_polygon_lvl10", "boundary_polygon_lvl2",
    "boundary_polygon_lvl3", "boundary_polygon_lvl4", "boundary_polygon_lvl5",
    "boundary_polygon_lvl6", "boundary_polygon_lvl7", "boundary_polygon_lvl8",
    "building_point", "building_polygon", "cutline_line", "elevation_line",
    "elevation_point", "highway_crossing_point", "highway_line",
    "island_polygon", "land", "landuse_polygon", "milestone_point",
    "nature_reserve_polygon", "parking_polygon", "pipeline_line",
    "poi_point", "poi_polygon", "port_point", "port_polygon",
    "power_line", "power_point", "public_transport_line",
    "public_transport_point", "railway_line", "railway_platform_polygon",
    "railway_station_point", "settlement_point", "settlement_polygon",
    "subway_entrance_point", "surface_polygon", "vegetation_polygon",
    "water_line", "water_point", "water_polygon",
]

# No FK constraint at the DB level (keeps this independent of which user
# table/app you're using) - wired up as a ForeignKey with db_constraint=False
# at the Django model level instead.
ALTER_SQL = """
ALTER TABLE "public"."{table}"
    ADD COLUMN IF NOT EXISTS "source" VARCHAR(50) NOT NULL DEFAULT 'nextgis',
    ADD COLUMN IF NOT EXISTS "version" INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS "needs_review" BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    ADD COLUMN IF NOT EXISTS "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    ADD COLUMN IF NOT EXISTS "updated_by_id" INTEGER NULL;
"""


class Command(BaseCommand):
    help = "Add version/needs_review/updated_by tracking columns to all imported NextGIS tables."

    def handle(self, *args, **options):
        with connection.cursor() as cur:
            for table in TABLE_NAMES:
                try:
                    cur.execute(ALTER_SQL.format(table=table))
                    self.stdout.write(self.style.SUCCESS(f"OK: {table}"))
                except Exception as exc:
                    self.stderr.write(f"FAILED: {table} - {exc}")
                    connection.rollback()

        self.stdout.write(self.style.SUCCESS(f"\nDone: {len(TABLE_NAMES)} tables processed."))