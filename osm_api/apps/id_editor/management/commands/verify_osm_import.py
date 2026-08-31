"""
Django management command to sanity-check a raw OSM PBF import.

Usage:
    Place this file at:
        apps/id_editor/management/commands/verify_osm_import.py
    (create the `management/commands/` folders with empty __init__.py files
    if they don't exist yet)

    Then run:
        python manage.py verify_osm_import

Checks performed:
    1. Row counts for all core tables
    2. Ways with fewer than 2 nodes (geometrically invalid)
    3. Duplicate (way_id, sequence_id) pairs in OsmWayNode
    4. way_nodes pointing to a node_id that doesn't exist in OsmNode
    5. Nodes with lat/lon = 0,0 ("null island" - usually a parsing bug)
    6. Bounding box check against Uzbekistan's real extent
    7. Top 20 most common tag keys (sanity check: building/highway should
       dominate)
    8. Sample of Cyrillic tag values, to catch mojibake/encoding issues
    9. Percentage of "building" ways that are properly closed rings
       (first node == last node), since unclosed buildings won't render
       as filled polygons in MapLibre/iD
"""

from django.core.management.base import BaseCommand
from django.db import connection


# Uzbekistan's real bounding box (lon_min, lat_min, lon_max, lat_max),
# with a small margin. Anything outside this is a sign of a bad import
# (wrong extract, corrupted geometry, or lon/lat swapped).
UZ_BBOX = (55.5, 37.0, 73.5, 45.8)


class Command(BaseCommand):
    help = "Sanity-check the OSM PBF import (nodes, ways, tags, geometry)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 1. Row counts ===\n"))
        self._counts()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 2. Ways with <2 nodes ===\n"))
        self._invalid_ways()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 3. Duplicate (way, sequence_id) ===\n"))
        self._duplicate_waynodes()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 4. Dangling way_node -> node references ===\n"))
        self._dangling_waynodes()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 5. Null-island nodes (lat=0, lon=0) ===\n"))
        self._null_island()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 6. Bounding box check ===\n"))
        self._bbox_check()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 7. Top 20 tag keys (nodes + ways) ===\n"))
        self._top_tags()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 8. Cyrillic tag value sample ===\n"))
        self._cyrillic_sample()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 9. Building ring closure ===\n"))
        self._building_closure()

        self.stdout.write(self.style.SUCCESS("\nDone.\n"))

    # ------------------------------------------------------------------

    def _fetch(self, sql, params=None):
        with connection.cursor() as cur:
            cur.execute(sql, params or [])
            columns = [c[0] for c in cur.description] if cur.description else []
            rows = cur.fetchall()
        return columns, rows

    def _print_rows(self, columns, rows):
        if not rows:
            self.stdout.write("  (no rows)")
            return
        for row in rows:
            line = "  " + " | ".join(str(v) for v in row)
            self.stdout.write(line)

    # ------------------------------------------------------------------

    def _counts(self):
        tables = [
            "id_editor_osmnode",
            "id_editor_osmway",
            "id_editor_osmwaynode",
            "id_editor_osmnodetag",
            "id_editor_osmwaytag",
        ]
        # NOTE: adjust table names above if your app_label/db_table differs
        # from the default Django naming convention (<app_label>_<modelname>).
        for table in tables:
            try:
                cols, rows = self._fetch(f"SELECT count(*) FROM {table}")
                self.stdout.write(f"  {table}: {rows[0][0]:,}")
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  {table}: ERROR - {exc}"))
                connection.rollback()

    def _invalid_ways(self):
        sql = """
            SELECT w.id, count(wn.id) AS node_count
            FROM id_editor_osmway w
            JOIN id_editor_osmwaynode wn ON wn.way_id = w.id
            GROUP BY w.id
            HAVING count(wn.id) < 2
            LIMIT 20
        """
        cols, rows = self._fetch(sql)
        self._print_rows(cols, rows)
        if len(rows) == 20:
            self.stdout.write("  (showing first 20 only, there may be more)")

    def _duplicate_waynodes(self):
        sql = """
            SELECT way_id, sequence_id, count(*)
            FROM id_editor_osmwaynode
            GROUP BY way_id, sequence_id
            HAVING count(*) > 1
            LIMIT 20
        """
        cols, rows = self._fetch(sql)
        self._print_rows(cols, rows)

    def _dangling_waynodes(self):
        sql = """
            SELECT count(*)
            FROM id_editor_osmwaynode wn
            LEFT JOIN id_editor_osmnode n ON n.id = wn.node_id
            WHERE n.id IS NULL
        """
        cols, rows = self._fetch(sql)
        self.stdout.write(f"  dangling references: {rows[0][0]:,}")

    def _null_island(self):
        sql = """
            SELECT count(*)
            FROM id_editor_osmnode
            WHERE lat = 0 AND lon = 0
        """
        cols, rows = self._fetch(sql)
        self.stdout.write(f"  nodes at (0,0): {rows[0][0]:,}")

    def _bbox_check(self):
        lon_min, lat_min, lon_max, lat_max = UZ_BBOX
        sql = """
            SELECT count(*)
            FROM id_editor_osmnode
            WHERE lon < %s OR lon > %s OR lat < %s OR lat > %s
        """
        cols, rows = self._fetch(sql, [lon_min, lon_max, lat_min, lat_max])
        out_of_bbox = rows[0][0]
        self.stdout.write(f"  nodes outside Uzbekistan bbox {UZ_BBOX}: {out_of_bbox:,}")

        cols, rows = self._fetch("""
            SELECT min(lon), max(lon), min(lat), max(lat) FROM id_editor_osmnode
        """)
        self.stdout.write(f"  actual extent (lon_min, lon_max, lat_min, lat_max): {rows[0]}")

    def _top_tags(self):
        sql = """
            SELECT k, count(*) AS cnt FROM (
                SELECT k FROM id_editor_osmnodetag
                UNION ALL
                SELECT k FROM id_editor_osmwaytag
            ) t
            GROUP BY k
            ORDER BY cnt DESC
            LIMIT 20
        """
        cols, rows = self._fetch(sql)
        self._print_rows(cols, rows)

    def _cyrillic_sample(self):
        # name:uz-Cyrl / name:ru / name are common tags carrying Cyrillic text
        sql = """
            SELECT k, v FROM id_editor_osmwaytag
            WHERE v ~ '[А-Яа-яЁёЎўҚқҒғҲҳ]'
            LIMIT 10
        """
        cols, rows = self._fetch(sql)
        self._print_rows(cols, rows)
        self.stdout.write(
            "  ^ check these render correctly in your terminal/editor. "
            "If you see '?' or mojibake here already, the corruption "
            "happened at import/DB level, not in the frontend."
        )

    def _building_closure(self):
        sql = """
            WITH building_ways AS (
                SELECT DISTINCT way_id FROM id_editor_osmwaytag WHERE k = 'building'
            ),
            endpoints AS (
                SELECT wn.way_id,
                       min(wn.sequence_id) AS first_seq,
                       max(wn.sequence_id) AS last_seq
                FROM id_editor_osmwaynode wn
                JOIN building_ways bw ON bw.way_id = wn.way_id
                GROUP BY wn.way_id
            ),
            first_last AS (
                SELECT e.way_id,
                       f.node_id AS first_node,
                       l.node_id AS last_node
                FROM endpoints e
                JOIN id_editor_osmwaynode f ON f.way_id = e.way_id AND f.sequence_id = e.first_seq
                JOIN id_editor_osmwaynode l ON l.way_id = e.way_id AND l.sequence_id = e.last_seq
            )
            SELECT
                count(*) AS total_buildings,
                count(*) FILTER (WHERE first_node = last_node) AS closed_buildings
            FROM first_last
        """
        cols, rows = self._fetch(sql)
        total, closed = rows[0]
        if total:
            pct = 100.0 * closed / total
            self.stdout.write(f"  total building ways: {total:,}")
            self.stdout.write(f"  closed rings: {closed:,} ({pct:.2f}%)")
            if pct < 99:
                self.stdout.write(self.style.WARNING(
                    "  Significant number of unclosed buildings — these won't "
                    "render as filled polygons. Often caused by ways that "
                    "cross the extract boundary and got dropped in `way()` "
                    "because not all referenced nodes were in node_id_map."
                ))
        else:
            self.stdout.write("  no ways tagged building=* found")