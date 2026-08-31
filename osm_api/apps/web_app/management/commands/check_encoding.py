from django.core.management.base import BaseCommand
from apps.web_app.models import (
    HighwayLine, BuildingPolygon, LandusePolygon,
    WaterPolygon, WaterLine, PoiPoint, SettlementPoint, SettlementPolygon,
)


class Command(BaseCommand):
    help = "Diagnostic: counts clean vs corrupted (mojibake) name values across tables."

    def handle(self, *args, **options):
        models_to_check = [
            ("highway_line", HighwayLine),
            ("building_polygon", BuildingPolygon),
            ("landuse_polygon", LandusePolygon),
            ("water_polygon", WaterPolygon),
            ("water_line", WaterLine),
            ("poi_point", PoiPoint),
            ("settlement_point", SettlementPoint),
            ("settlement_polygon", SettlementPolygon),
        ]

        for label, model in models_to_check:
            total = 0
            corrupted = 0
            samples = []

            for row in model.objects.exclude(name__isnull=True).exclude(name=''):
                total += 1
                if any(ch in row.name for ch in '├╫┬СРв'):
                    corrupted += 1
                    if len(samples) < 3:
                        samples.append((row.pk, row.name))

            self.stdout.write(f"\n=== {label} ===")
            self.stdout.write(f"Total: {total}, Corrupted: {corrupted}")
            for pk, name in samples:
                self.stdout.write(f"  id={pk}: {name!r}")