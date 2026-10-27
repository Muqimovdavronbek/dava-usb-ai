$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Temp = $null
$Failed = $false
try {
    $Manifest = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'parts.json') | ConvertFrom-Json
    $Candidates = @($Root, (Split-Path -Parent $Root), (Split-Path -Parent (Split-Path -Parent $Root)))
    $Folder = $null
    foreach ($Candidate in $Candidates) {
        $Complete = $true
        foreach ($Part in $Manifest.parts) {
            if (-not (Test-Path -LiteralPath (Join-Path $Candidate $Part.name))) { $Complete = $false }
        }
        if ($Complete) { $Folder = $Candidate; break }
    }
    if (-not $Folder) { throw 'Hamma 5 qismni bitta papkaga yuklang. Yigish ZIPini shu papkaga oching.' }
    $Target = Join-Path $Folder $Manifest.folder
    if (Test-Path -LiteralPath $Target) { throw 'Dava_USB_AI papkasi allaqachon bor. Avval uni boshqa joyga kochiring yoki nomini ozgartiring.' }
    foreach ($Part in $Manifest.parts) {
        if ((Get-Item -LiteralPath (Join-Path $Folder $Part.name)).Length -ne $Part.size) { throw ($Part.name + ' toliq yuklanmagan. Shu qismni qayta yuklang.') }
    }
    Write-Host "`nDAVA USB AI - TOLIQ OFLAYN PAKETNI YIGISH`n" -ForegroundColor Cyan
    Write-Host 'Kompyuter diskida kamida 5.1 GB bosh joy kerak. Yigishni fleshkada bajarmang.'
    $Temp = Join-Path $Folder ('Dava_AI_yigilyapti_' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $Temp | Out-Null
    $Archive = Join-Path $Temp $Manifest.archive_name
    $Output = [System.IO.File]::Open($Archive, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
    try {
        $Index = 0
        foreach ($Part in $Manifest.parts) {
            $Index++
            $Path = Join-Path $Folder $Part.name
            Write-Host "[$Index/5] $($Part.name) tekshirilyapti va birlashtirilyapti..."
            if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Part.sha256) { throw ($Part.name + ' buzilgan. Faqat shu qismni qayta yuklang.') }
            $InputStream = [System.IO.File]::OpenRead($Path)
            try { $InputStream.CopyTo($Output, 8388608) } finally { $InputStream.Dispose() }
        }
    } finally { $Output.Dispose() }
    if ((Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Manifest.archive_sha256) { throw 'Yigilgan arxiv nazorat summasi mos emas.' }
    Write-Host 'Arxiv togri. Tayyor dastur papkasi chiqarilyapti...'
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($Archive, $Temp)
    Move-Item -LiteralPath (Join-Path $Temp $Manifest.folder) -Destination $Target
    Write-Host "`nTAYYOR! $Target" -ForegroundColor Green
    Write-Host 'Endi shu Dava_USB_AI papkasini butunligicha fleshkaga kochiring.'
    Write-Host 'Fleshka papkasidagi BOSHLASH_WINDOWS.cmd faylini oching.'
    Write-Host '5 qismni fleshkaga kochirish shart emas. Model tayyor papkaning ichida.'
} catch {
    Write-Host ("`nXATO: " + $_.Exception.Message) -ForegroundColor Red
    $Failed = $true
} finally {
    if ($Temp -and (Test-Path -LiteralPath $Temp)) { Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue }
}
if ($Failed) { exit 1 }
