"""
One-off diagnostic script: counts how many `name` values in highway_line
look clean vs corrupted. Run via `python manage.py shell < fix_encoding_check.py`
so Python (not the Windows console) handles all Unicode comparisons —
avoids re-encoding issues that happen when typing multi-byte characters
directly into an interactive psql session on Windows.
"""
import django
django.setup()

from apps.web_app.models import HighwayLine

total = 0
clean = 0
corrupted_samples = []

for row in HighwayLine.objects.exclude(name__isnull=True).exclude(name=''):
    total += 1
    # Corrupted rows typically contain box-drawing / control-picture
    # characters left behind by repeated mis-decoding (mojibake).
    if any(ch in row.name for ch in '├╫┬СРв'):
        if len(corrupted_samples) < 10:
            corrupted_samples.append((row.pk, row.name))
    else:
        clean += 1

print(f"Total non-empty names: {total}")
print(f"Clean-looking: {clean}")
print(f"Corrupted-looking: {total - clean}")
print("\nSample corrupted rows:")
for pk, name in corrupted_samples:
    print(f"  id={pk}: {name!r}")