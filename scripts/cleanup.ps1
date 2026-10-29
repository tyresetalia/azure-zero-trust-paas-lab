# ==============================================================================
# Azure Zero-Trust PaaS Lab - Opruimscript
# Verwijdert alle aangemaakte resources om onnodige Azure kosten te voorkomen.
# ==============================================================================

param(
    [string]$ResourceGroupName = "rg-zerotrust-paas-lab"
)

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Azure Zero-Trust PaaS Lab - Resource Cleanup        " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

$confirmation = Read-Host "Weet je zeker dat je alle resources in '$ResourceGroupName' wilt verwijderen? (y/n)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Opruimactie geannuleerd." -ForegroundColor Yellow
    exit
}

Write-Host "`n[1/1] Resource Group '$ResourceGroupName' en alle resources verwijderen..." -ForegroundColor Yellow
az group delete --name $ResourceGroupName --yes --no-wait

Write-Host "`nVerwijdering is op de achtergrond gestart!" -ForegroundColor Green
Write-Host "Binnen enkele minuten zijn alle resources en bijbehorende kosten gewist." -ForegroundColor Green
