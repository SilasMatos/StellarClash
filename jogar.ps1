Write-Host "=== Astromarujo ===" -ForegroundColor Cyan
Write-Host "Iniciando o jogo..." -ForegroundColor Green
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

try {
    & "C:/Users/Silas/AppData/Local/Programs/Python/Python313/python.exe" "astromarujo.py"
}
catch {
    Write-Host "Erro ao executar o jogo: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
