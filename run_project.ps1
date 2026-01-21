Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  AI VISUAL INSIGHT PRO - Advanced Edition" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features:" -ForegroundColor Yellow
Write-Host "  🎤 Speech-to-Text Transcription" -ForegroundColor Green
Write-Host "  📝 AI-Powered Summarization" -ForegroundColor Green
Write-Host "  🛡️ Content Moderation & Safety Analysis" -ForegroundColor Green
Write-Host "  📊 Video Quality Assessment" -ForegroundColor Green
Write-Host "  ⚡ Lightning-Fast Processing" -ForegroundColor Green
Write-Host ""
Write-Host "Starting application..." -ForegroundColor White
Write-Host ""

$env:STREAMLIT_SERVER_HEADLESS = "true"
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"

# Use workspace virtual environment Python explicitly to avoid PATH issues
& "D:/Major Final Year Project/.venv/Scripts/python.exe" -m streamlit run "D:/Major Final Year Project/app_pro.py" --server.port=8501

Write-Host ""
Write-Host "Application closed." -ForegroundColor Yellow
