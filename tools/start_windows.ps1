$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Engine = Join-Path $Root 'bin\llamafile.exe'
$Model = Join-Path $Root 'models\Qwen3-4B-Q4_K_M.gguf'
$Proc = $null
$OldTemplate = $env:LLAMA_ARG_CHAT_TEMPLATE_KWARGS
$Failed = $false
try {
    if (-not [Environment]::Is64BitOperatingSystem) { throw '64-bit Windows kerak.' }
    if (-not (Test-Path -LiteralPath $Engine)) { throw 'bin\llamafile.exe topilmadi. ZIPni toliq oching.' }
    if (-not (Test-Path -LiteralPath $Model)) { throw 'Model topilmadi. ZIPni toliq oching.' }
    if ((Get-Item -LiteralPath $Model).Length -ne 2497280256) { throw 'Model toliq emas. ZIPni qayta oching.' }
    if ((Get-FileHash -LiteralPath $Engine -Algorithm SHA256).Hash.ToLowerInvariant() -ne '756bf97febae557084e8ced9bde7a1cb0c7f6ce778530d582afa219406237a50') {
        throw 'Dastur fayli buzilgan. ZIPni qayta oching.'
    }
    $Port = 0
    $Candidates = 8765..8799
    if ($env:DAVA_PORT) { $Candidates = @([int]$env:DAVA_PORT) }
    foreach ($Candidate in $Candidates) {
        $Listener = $null
        try {
            $Listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Candidate)
            $Listener.Start()
            $Port = $Candidate
            break
        } catch { } finally { if ($Listener) { $Listener.Stop() } }
    }
    if (-not $Port) { throw '8765-8799 portlar band. Oldingi AI oynasini yoping.' }
    $Url = "http://127.0.0.1:$Port/"
    $Logs = Join-Path $Root 'logs'
    New-Item -ItemType Directory -Force -Path $Logs | Out-Null
    $OutLog = Join-Path $Logs 'windows-stdout.log'
    $ErrLog = Join-Path $Logs 'windows-stderr.log'
    $Threads = [Math]::Max(1, [Math]::Min(4, [Environment]::ProcessorCount))
    $env:LLAMA_ARG_CHAT_TEMPLATE_KWARGS = '{"enable_thinking":false}'
    # All arguments below are relative paths without spaces; WorkingDirectory is the USB folder.
    $Arguments = @('--server', '-m', 'models\Qwen3-4B-Q4_K_M.gguf', '--host', '127.0.0.1',
                   '--port', "$Port", '--path', 'web', '--alias', 'Dava-USB-AI',
                   '--ctx-size', '4096', '--parallel', '1', '--threads', "$Threads",
                   '--batch-size', '256', '--ubatch-size', '128', '--n-predict', '1024',
                   '--gpu', 'disable', '--n-gpu-layers', '0', '--offline', '--no-slots',
                   '--no-webui-mcp-proxy', '--cors-origins', $Url.TrimEnd('/'), '--nologo')
    Write-Host "`nDAVA USB AI | Qwen3 4B | Oflayn`n" -ForegroundColor Cyan
    Write-Host 'Model ochilyapti. Fleshka tezligiga qarab bir necha daqiqa ketishi mumkin.'
    Write-Host 'Tayyor bolganda chat brauzerda ochiladi. Toxtatish: Ctrl+C.'
    $Proc = Start-Process -FilePath $Engine -ArgumentList $Arguments -WorkingDirectory $Root -NoNewWindow -PassThru -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog
    $Ready = $false
    $Timer = [Diagnostics.Stopwatch]::StartNew()
    $LastNotice = 0
    while ($Timer.Elapsed.TotalSeconds -lt 600) {
        $Proc.Refresh()
        if ($Proc.HasExited) { break }
        $Response = $null
        try {
            $Request = [System.Net.HttpWebRequest]::Create($Url + 'health')
            $Request.Proxy = $null
            $Request.Timeout = 1000
            $Response = $Request.GetResponse()
            if ([int]$Response.StatusCode -eq 200) { $Ready = $true }
        } catch { } finally { if ($Response) { $Response.Close() } }
        if ($Ready) { break }
        if ($Timer.Elapsed.TotalSeconds - $LastNotice -ge 15) {
            Write-Host 'Hali yuklanyapti...'
            $LastNotice = $Timer.Elapsed.TotalSeconds
        }
        Start-Sleep -Milliseconds 500
    }
    if (-not $Ready) {
        if (Test-Path -LiteralPath $ErrLog) { Get-Content -LiteralPath $ErrLog -Tail 15 | Write-Host }
        throw 'AI ishga tushmadi. logs\windows-stderr.log faylini tekshiring.'
    }
    Write-Host "`nTAYYOR: $Url" -ForegroundColor Green
    Write-Host 'Bu oynani ochiq qoldiring. Toxtatish: Ctrl+C.'
    if ($env:DAVA_NO_BROWSER -ne '1') { Start-Process $Url }
    while (-not $Proc.HasExited) { Start-Sleep -Milliseconds 500; $Proc.Refresh() }
    if ($Proc.ExitCode -ne 0) { throw "AI toxtadi. Kod: $($Proc.ExitCode). logs papkasini tekshiring." }
} catch {
    Write-Host ("`nXATO: " + $_.Exception.Message) -ForegroundColor Red
    $Failed = $true
} finally {
    if ($Proc) {
        $Proc.Refresh()
        if (-not $Proc.HasExited) { Stop-Process -Id $Proc.Id -ErrorAction SilentlyContinue }
    }
    $env:LLAMA_ARG_CHAT_TEMPLATE_KWARGS = $OldTemplate
}
if ($Failed) { exit 1 }
