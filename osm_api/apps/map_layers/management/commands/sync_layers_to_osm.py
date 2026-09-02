"""
sync_layers_to_osm.py

Reads every concrete TrackingMixin layer table (46 total) and writes
their geometry + attributes into osm_nodes / osm_ways / osm_way_nodes /
osm_node_tags / osm_way_tags so that /api/0.6/map can serve them as
editable OSM data in iD editor.

Usage:
    python manage.py sync_layers_to_osm               # import all tables
    python manage.py sync_layers_to_osm --clear       # truncate first
    python manage.py sync_layers_to_osm --table highway_line
    python manage.py sync_layers_to_osm --limit 1000  # first N rows per table

Geometry mapping:
    MultiPoint   -> OsmNode per sub-point
    MultiLine    -> OsmWay per sub-line, one OsmNode per vertex
    MultiPolygon -> OsmWay per outer ring, one OsmNode per unique vertex
                   (ring is closed: first way-node == last way-node)
"""

import inspect

import psycopg2.extras
from django.core.management.base import BaseCommand
from django.contrib.gis.db.models import (
    MultiPointField, MultiLineStringField, MultiPolygonField,
    PointField, LineStringField, PolygonField,
)
from django.db import connection
from django.utils import timezone

from apps.map_layers import models as layer_models

# ──────────────────────────────────────────────
# Fields that must NOT become OSM tag k/v pairs
# ──────────────────────────────────────────────
_SKIP = frozenset({
    'fid', 'geom', 'osm_type',
    'edit_source', 'version', 'needs_review',
    'created_at', 'updated_at', 'updated_by', 'updated_by_id',
})

# Abbreviated NextGIS column names → proper OSM tag keys
_REMAP = {
    'a_strt':     'addr:street',
    'a_sbrb':     'addr:suburb',
    'a_hsnmbr':   'addr:housenumber',
    'a_place':    'addr:place',
    'a_pstcd':    'addr:postcode',
    'b_levels':   'building:levels',
    'name_en':    'name:en',
    'aerod_type': 'aerodrome:type',
    'mountain_p': 'mountain_pass',
    'crossing_r': 'crossing:ref',
    'admin_lvl':  'admin_level',
    'rsdntl':     'residential',
    'public_tra': 'public_transport',
    'from_field': 'from',
    'admin_l1':   'addr:district',
}

_DEFAULT_BATCH = 200


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _discover_models(only_table=''):
    """Return all concrete (non-abstract) TrackingMixin subclasses, sorted by db_table."""
    result = []
    for _, obj in inspect.getmembers(layer_models, inspect.isclass):
        if (issubclass(obj, layer_models.TrackingMixin)
                and obj is not layer_models.TrackingMixin
                and not obj._meta.abstract):
            if only_table and obj._meta.db_table != only_table:
                continue
            result.append(obj)
    return sorted(result, key=lambda m: m._meta.db_table)


def _geom_kind(model):
    """Return 'point', 'line', or 'polygon', or None if unrecognised."""
    try:
        f = model._meta.get_field('geom')
    except Exception:
        return None
    if isinstance(f, (MultiPointField, PointField)):
        return 'point'
    if isinstance(f, (MultiLineStringField, LineStringField)):
        return 'line'
    if isinstance(f, (MultiPolygonField, PolygonField)):
        return 'polygon'
    return None


def _tag_fields(model):
    """Return list of (python_field_name, osm_tag_key) for taggable fields."""
    result = []
    for field in model._meta.fields:
        name = field.name
        if name in _SKIP:
            continue
        if getattr(field, 'related_model', None) is not None:
            continue
        key = _REMAP.get(name, name)
        result.append((name, key))
    return result


def _sub_geoms(geom):
    """Flatten any Multi* geometry to a list of simple geometries.

    Django's GEOS collections are iterable directly (list(geom) works);
    simple geometries are returned as a one-element list.
    """
    if geom is None:
        return []
    try:
        # Multi* geometries support iteration and have num_geom > 1
        if geom.num_geom >= 1:
            return [geom[i] for i in range(geom.num_geom)]
    except Exception:
        pass
    return [geom]


def _get_tags(obj, tag_fields, layer_name):
    """Return {osm_tag_key: str_value} for non-null fields + source:layer."""
    tags = {}
    for fname, key in tag_fields:
        val = getattr(obj, fname, None)
        if val is not None and str(val).strip():
            tags[key] = str(val)
    tags['source:layer'] = layer_name
    return tags


def _insert_nodes(cur, coords, now):
    """
    Bulk-insert nodes for a list of (lat, lon) tuples.
    Returns list of new node IDs in the same order.
    """
    psycopg2.extras.execute_values(
        cur,
        """INSERT INTO osm_nodes (version, visible, lat, lon, timestamp, geom)
           VALUES %s RETURNING id""",
        [(1, True, lat, lon, now, lon, lat) for lat, lon in coords],
        template="(%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
        page_size=5000,
    )
    return [r[0] for r in cur.fetchall()]


def _insert_ways(cur, count, now):
    """Bulk-insert `count` ways. Returns list of new way IDs."""
    psycopg2.extras.execute_values(
        cur,
        "INSERT INTO osm_ways (version, visible, timestamp) VALUES %s RETURNING id",
        [(1, True, now)] * count,
        page_size=5000,
    )
    return [r[0] for r in cur.fetchall()]


def _insert_way_nodes(cur, rows):
    """rows: list of (way_id, sequence_id, node_id)"""
    if not rows:
        return
    psycopg2.extras.execute_values(
        cur,
        "INSERT INTO osm_way_nodes (way_id, sequence_id, node_id) VALUES %s",
        rows,
        page_size=10000,
    )


def _insert_node_tags(cur, rows):
    """rows: list of (node_id, k, v)"""
    if not rows:
        return
    psycopg2.extras.execute_values(
        cur,
        "INSERT INTO osm_node_tags (node_id, k, v) VALUES %s ON CONFLICT DO NOTHING",
        rows,
        page_size=5000,
    )


def _insert_way_tags(cur, rows):
    """rows: list of (way_id, k, v)"""
    if not rows:
        return
    psycopg2.extras.execute_values(
        cur,
        "INSERT INTO osm_way_tags (way_id, k, v) VALUES %s ON CONFLICT DO NOTHING",
        rows,
        page_size=5000,
    )


# ──────────────────────────────────────────────
# Command
# ──────────────────────────────────────────────

class Command(BaseCommand):
    help = "Sync all 46 layer tables into osm_nodes/osm_ways for iD editor display."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='TRUNCATE all osm_* tables before importing (resets sequences too).',
        )
        parser.add_argument(
            '--table', type=str, default='',
            help='Import only this db_table (e.g. --table highway_line).',
        )
        parser.add_argument(
            '--batch', type=int, default=_DEFAULT_BATCH,
            help=f'Source features per flush batch (default {_DEFAULT_BATCH}).',
        )
        parser.add_argument(
            '--limit', type=int, default=0,
            help='Max rows to import per table (0 = all). Useful for testing.',
        )

    def handle(self, *args, **options):
        models = _discover_models(options['table'].strip())
        if not models:
            self.stderr.write(self.style.ERROR('No matching models found.'))
            return

        with connection.cursor() as django_cur:
            cur = django_cur.cursor  # raw psycopg2 cursor

            if options['clear']:
                self._clear(cur)

            for model in models:
                self._import_model(cur, model, options['batch'], options['limit'])

            self._ensure_indexes(cur)
            cur.connection.commit()

        self.stdout.write(self.style.SUCCESS('\nAll done.'))

    # ------------------------------------------------------------------

    def _clear(self, cur):
        self.stdout.write('Truncating OSM tables...')
        cur.execute(
            'TRUNCATE osm_way_tags, osm_node_tags, osm_way_nodes, '
            'osm_ways, osm_nodes RESTART IDENTITY CASCADE'
        )
        self.stdout.write('  cleared.\n')

    def _ensure_indexes(self, cur):
        self.stdout.write('Creating spatial index on osm_nodes.geom (if missing)...')
        cur.execute(
            'CREATE INDEX IF NOT EXISTS osm_nodes_geom_gist '
            'ON osm_nodes USING GIST (geom)'
        )

    def _import_model(self, cur, model, batch_size, limit):
        table = model._meta.db_table
        kind = _geom_kind(model)
        if kind is None:
            self.stderr.write(f'  {table}: unrecognised geom type — skipped')
            return

        tag_fields = _tag_fields(model)
        qs = model.objects.all()
        if limit:
            qs = qs[:limit]
        total = qs.count()
        self.stdout.write(f'\n{table}  ({kind}, {total:,} rows)')

        imported = 0
        batch = []
        for obj in qs.iterator(chunk_size=batch_size):
            if obj.geom is None:
                continue
            batch.append(obj)
            if len(batch) >= batch_size:
                self._flush(cur, kind, tag_fields, table, batch)
                imported += len(batch)
                self.stdout.write(f'  {imported:,}/{total:,}', ending='\r')
                self.stdout.flush()
                batch = []

        if batch:
            self._flush(cur, kind, tag_fields, table, batch)
            imported += len(batch)

        self.stdout.write(self.style.SUCCESS(f'  {table}: {imported:,} features imported'))

    def _flush(self, cur, kind, tag_fields, table_name, features):
        if kind == 'point':
            self._flush_points(cur, tag_fields, table_name, features)
        else:
            self._flush_ways(cur, kind, tag_fields, table_name, features)

    # ------------------------------------------------------------------
    # Point features: each sub-point → one OsmNode
    # ------------------------------------------------------------------

    def _flush_points(self, cur, tag_fields, table_name, features):
        now = timezone.now()
        coords = []
        feat_ranges = []

        for obj in features:
            start = len(coords)
            for pt in _sub_geoms(obj.geom):
                coords.append((float(pt.y), float(pt.x)))  # (lat, lon)
            end = len(coords)
            if end > start:
                feat_ranges.append((start, end, obj))

        if not coords:
            return

        node_ids = _insert_nodes(cur, coords, now)

        tag_rows = []
        for start, end, obj in feat_ranges:
            tags = _get_tags(obj, tag_fields, table_name)
            for nid in node_ids[start:end]:
                for k, v in tags.items():
                    tag_rows.append((nid, k, v))
        _insert_node_tags(cur, tag_rows)

    # ------------------------------------------------------------------
    # Line/Polygon features: each geometry part → one OsmWay
    # ------------------------------------------------------------------

    def _flush_ways(self, cur, kind, tag_fields, table_name, features):
        now = timezone.now()
        all_coords = []   # flat (lat, lon) list
        # (coord_start, coord_count, close_ring, obj)
        way_meta = []

        for obj in features:
            for part in _sub_geoms(obj.geom):
                try:
                    if kind == 'polygon':
                        # Use exterior ring only; drop the duplicated closing coord.
                        ring = part.exterior_ring
                        raw = [(c[1], c[0]) for c in ring.coords]
                        # LinearRing is closed (first == last), strip the duplicate.
                        if len(raw) > 1 and raw[0] == raw[-1]:
                            raw = raw[:-1]
                        close_ring = True
                    else:
                        raw = [(c[1], c[0]) for c in part.coords]
                        close_ring = False
                except Exception:
                    continue

                if len(raw) < 2:
                    continue

                start = len(all_coords)
                all_coords.extend(raw)
                way_meta.append((start, len(all_coords), close_ring, obj))

        if not all_coords or not way_meta:
            return

        node_ids = _insert_nodes(cur, all_coords, now)
        way_ids = _insert_ways(cur, len(way_meta), now)

        wn_rows = []
        tag_rows = []
        for way_id, (start, end, close_ring, obj) in zip(way_ids, way_meta):
            segment = node_ids[start:end]
            if not segment:
                continue
            if close_ring:
                # First node and last node must be the same OsmNode row.
                segment = segment + [segment[0]]
            for seq, nid in enumerate(segment):
                wn_rows.append((way_id, seq, nid))

            tags = _get_tags(obj, tag_fields, table_name)
            for k, v in tags.items():
                tag_rows.append((way_id, k, v))

        _insert_way_nodes(cur, wn_rows)
        _insert_way_tags(cur, tag_rows)
