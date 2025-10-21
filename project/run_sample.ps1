param(
    [string]$videoPath = "",
    [string]$outdir = "D:\maj pro\project\outputs"
)

if (-not $videoPath) {
    Write-Host "Usage: .\run_sample.ps1 -videoPath 'C:\path\to\video.mp4'"
    exit 1
}

# Activate venv if present
$venv = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venv) {
    . $venv
}

python "$PSScriptRoot\main.py" --input $videoPath --outdir $outdir
