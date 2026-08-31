"""
apps/map_layers/management/commands/fix_tracking_column_names.py

Renames our tracking "source" column to "edit_source" everywhere, to avoid
colliding with layers that have their own native "source" attribute
(discovered: milestone_point already had one, so our earlier
ADD COLUMN IF NOT EXISTS silently no-opped there).

Usage:
    python manage.py fix_tracking_column_names
"""

from django.core.management.base import BaseCommand
from django.db import connection

# All tables except milestone_point already got our tracking "source"
# column successfully - just rename it.
TABLES_TO_RENAME = [
    "aerialway_line", "aerialway_point", "airport_line", "airport_polygon",
    "boundary_polygon", "boundary_polygon_lvl10", "boundary_polygon_lvl2",
    "boundary_polygon_lvl3", "boundary_polygon_lvl4", "boundary_polygon_lvl5",
    "boundary_polygon_lvl6", "boundary_polygon_lvl7", "boundary_polygon_lvl8",
    "building_point", "building_polygon", "cutline_line", "elevation_line",
    "elevation_point", "highway_crossing_point", "highway_line",
    "island_polygon", "land", "landuse_polygon",
    "nature_reserve_polygon", "parking_polygon", "pipeline_line",
    "poi_point", "poi_polygon", "port_point", "port_polygon",
    "power_line", "power_point", "public_transport_line",
    "public_transport_point", "railway_line", "railway_platform_polygon",
    "railway_station_point", "settlement_point", "settlement_polygon",
    "subway_entrance_point", "surface_polygon", "vegetation_polygon",
    "water_line", "water_point", "water_polygon",
]


class Command(BaseCommand):
    help = "Rename tracking 'source' column to 'edit_source' across all layer tables."

    def handle(self, *args, **options):
        with connection.cursor() as cur:
            for table in TABLES_TO_RENAME:
                try:
                    cur.execute(
                        f'ALTER TABLE "public"."{table}" '
                        f'RENAME COLUMN "source" TO "edit_source";'
                    )
                    self.stdout.write(self.style.SUCCESS(f"OK: {table}"))
                except Exception as exc:
                    self.stderr.write(f"FAILED: {table} - {exc}")
                    connection.rollback()

            # milestone_point never got the tracking column at all - add it
            # fresh under the new name, leaving its native "source" alone.
            try:
                cur.execute(
                    'ALTER TABLE "public"."milestone_point" '
                    'ADD COLUMN IF NOT EXISTS "edit_source" VARCHAR(50) '
                    "NOT NULL DEFAULT 'nextgis';"
                )
                self.stdout.write(self.style.SUCCESS("OK: milestone_point (added edit_source)"))
            except Exception as exc:
                self.stderr.write(f"FAILED: milestone_point - {exc}")
                connection.rollback()

        self.stdout.write(self.style.SUCCESS("\nDone."))