param(
    [string]$ResFile = "",
    [int]$TimeoutMs = 15000,
    [switch]$SingleShot,
    [switch]$AllowFocusPulse = $true,
    [switch]$Diagnostics
)

$pyScript = Join-Path $PSScriptRoot "nudge_moho.py"
$argsList = @($pyScript)
if ($ResFile) { $argsList += @("-resfile", $ResFile) }
$argsList += @("-timeoutms", [string]$TimeoutMs)
if ($SingleShot) { $argsList += "-singleshot" }
if ($Diagnostics) { $argsList += "-diagnostics" }
if (-not $AllowFocusPulse) { $argsList += "-nofocus" }
& python @argsList
exit $LASTEXITCODE
