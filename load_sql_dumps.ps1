# load_sql_dumps.ps1
#
# Loads every NextGIS .sql dump in the data folder directly into your
# existing PostGIS database via psql. Each file already contains its own
# DROP TABLE IF EXISTS ... CASCADE, so it's safe to re-run.
#
# Fill in the values below from osm_api/osm_api/settings.py DATABASES,
# then run:
#     .\load_sql_dumps.ps1

# ---- EDIT THESE ----
$PsqlPath = "psql"                      # or full path, e.g. "C:\Program Files\PostgreSQL\16\bin\psql.exe"
$DbHost   = "localhost"
$DbPort   = "5432"
$DbName   = "map_work_db"
$DbUser   = "postgres"
$DbPass   = "12345"
$DataDir  = "C:\Users\user\Desktop\practice\map_work\data"
# ---------------------

$env:PGPASSWORD = $DbPass

$sqlFiles = Get-ChildItem "$DataDir\*.sql" | Sort-Object Name
$total = $sqlFiles.Count
$failed = @()

Write-Host "Found $total .sql files to load into '$DbName'`n"

$i = 0
foreach ($file in $sqlFiles) {
    $i++
    Write-Host "[$i/$total] Loading $($file.Name) ..." -NoNewline

    & $PsqlPath -h $DbHost -p $DbPort -U $DbUser -d $DbName `
        -v ON_ERROR_STOP=1 -q -f $file.FullName 2>&1 | Out-Null

    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        $failed += $file.Name
    }
}

Write-Host "`n---"
Write-Host "Done: $($total - $failed.Count)/$total succeeded"
if ($failed.Count -gt 0) {
    Write-Host "Failed files:" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "  - $_" }
}

Remove-Item Env:\PGPASSWORD

# ---- Step 2: Add tracking columns via Django management commands ----
Write-Host "`nAdding tracking columns (edit_source, version, needs_review, ...)..."
$OsmApiDir = Split-Path $DataDir -Parent | Join-Path -ChildPath "osm_api"
$PythonExe = Join-Path $OsmApiDir "venv\Scripts\python.exe"
$ManagePy  = Join-Path $OsmApiDir "manage.py"

& $PythonExe $ManagePy add_layer_tracking_columns
& $PythonExe $ManagePy fix_tracking_column_names
& $PythonExe $ManagePy migrate --run-syncdb

Write-Host "Tracking columns added. DB restore complete." -ForegroundColor Green
