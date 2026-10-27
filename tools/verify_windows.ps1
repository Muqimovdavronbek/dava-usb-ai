$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Failed = $false
Write-Host 'Fayllar tekshirilyapti. Katta model tufayli bir oz kuting.'
foreach ($Line in Get-Content -LiteralPath (Join-Path $Root 'SHA256SUMS.txt')) {
    if ($Line -match '^([a-f0-9]{64})  (.+)$') {
        $Expected = $Matches[1]
        $Name = $Matches[2]
        $Path = Join-Path $Root $Name
        if (-not (Test-Path -LiteralPath $Path)) {
            Write-Host "YOQ: $Name" -ForegroundColor Red
            $Failed = $true
        } elseif ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Expected) {
            Write-Host "MOS EMAS: $Name" -ForegroundColor Red
            $Failed = $true
        } else { Write-Host "OK: $Name" -ForegroundColor Green }
    }
}
if ($Failed) { Write-Host 'Fayllar buzilgan yoki toliq emas. ZIPni qayta oching.'; exit 1 }
Write-Host 'Hammasi mos. BOSHLASH_WINDOWS.cmd faylini ochishingiz mumkin.' -ForegroundColor Green
