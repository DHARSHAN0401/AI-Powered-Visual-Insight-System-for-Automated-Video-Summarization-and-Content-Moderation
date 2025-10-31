Write-Host "Starting AI Visual Insight Pro..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$env:STREAMLIT_SERVER_HEADLESS = "true"
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"

python -m streamlit run app_advanced.py

Write-Host ""
Write-Host "Application closed." -ForegroundColor Yellow
