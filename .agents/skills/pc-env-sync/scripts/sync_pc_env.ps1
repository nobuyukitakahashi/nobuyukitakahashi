$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== [1/6] Detecting Workspace & Google Drive Paths ==="
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = (Resolve-Path (Join-Path $ScriptDir "..\..\..\..")).Path
$DriveRoot = Split-Path -Parent (Split-Path -Parent $WorkspaceRoot)
$ObsidianVaultPath = Join-Path $DriveRoot "obsidian\nobuyukitakahashi\nobuyukitakahashi"

Write-Host "  Workspace : $WorkspaceRoot"
Write-Host "  DriveRoot : $DriveRoot"
Write-Host "  VaultPath : $ObsidianVaultPath"

Write-Host "`n=== [2/6] Syncing Latest GitHub Repository (git pull) ==="
Push-Location $WorkspaceRoot
try {
    $ErrorActionPreference = "Continue"
    git pull origin main --ff-only 2>&1 | ForEach-Object { Write-Host "  $_" }
    $ErrorActionPreference = "Stop"
} catch {
    Write-Warning "git pull skipped: $_"
}
Pop-Location

Write-Host "`n=== [3/6] Syncing Global Skills (.gemini/config/skills) ==="
$GlobalSkillsDir = Join-Path $env:USERPROFILE ".gemini\config\skills"
if (-not (Test-Path $GlobalSkillsDir)) {
    New-Item -ItemType Directory -Path $GlobalSkillsDir -Force | Out-Null
}

$SkillsToSync = @(
    "obsidian-markdown",
    "obsidian-bases",
    "obsidian-cli",
    "json-canvas",
    "defuddle",
    "knap",
    "audio-meeting-minutes",
    "auto-git-sync",
    "wordpress-avada-maintenance",
    "adobe-illustrator",
    "pc-env-sync"
)

foreach ($skill in $SkillsToSync) {
    $src = Join-Path $WorkspaceRoot ".agents\skills\$skill"
    $dst = Join-Path $GlobalSkillsDir $skill
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $GlobalSkillsDir -Recurse -Force
        Write-Host "  [OK] Synced skill: $skill"
    }
}

$GlobalPluginsDir = Join-Path $env:USERPROFILE ".gemini\config\plugins"
if (-not (Test-Path $GlobalPluginsDir)) {
    New-Item -ItemType Directory -Path $GlobalPluginsDir -Force | Out-Null
}
$NotebookPluginSrc = Join-Path $WorkspaceRoot ".agents\plugins\notebooklm-plugin"
if (Test-Path $NotebookPluginSrc) {
    Copy-Item -Path $NotebookPluginSrc -Destination $GlobalPluginsDir -Recurse -Force
    Write-Host "  [OK] Synced global plugin: notebooklm-plugin"
}

Write-Host "`n=== [4/6] Verifying Obsidian MCP (@bitbonsai/mcpvault) & Blender MCP (mcp-for-blender) ==="
$NpmGlobalModules = (npm root -g).Trim()
$McpVaultScript = Join-Path $NpmGlobalModules "@bitbonsai\mcpvault\dist\server.js"
$NotebookLmMcpScript = Join-Path $NpmGlobalModules "notebooklm-mcp\dist\index.js"

if (-not (Test-Path $McpVaultScript)) {
    Write-Host "  Installing @bitbonsai/mcpvault globally..."
    npm install -g "@bitbonsai/mcpvault" | Out-Host
} else {
    Write-Host "  [OK] @bitbonsai/mcpvault already installed: $McpVaultScript"
}

if (-not (Test-Path $NotebookLmMcpScript)) {
    Write-Host "  Installing notebooklm-mcp globally..."
    npm install -g "notebooklm-mcp" | Out-Host
} else {
    Write-Host "  [OK] notebooklm-mcp already installed: $NotebookLmMcpScript"
}

$UvxCmd = Get-Command uvx -ErrorAction SilentlyContinue
if ($UvxCmd) {
    $UvxPath = $UvxCmd.Source
    Write-Host "  [OK] uvx detected for Blender MCP: $UvxPath"
} else {
    $FallbackUvx = Join-Path $env:USERPROFILE ".local\bin\uvx.exe"
    if (Test-Path $FallbackUvx) {
        $UvxPath = $FallbackUvx
        Write-Host "  [OK] uvx detected at fallback path: $UvxPath"
    } else {
        $UvxPath = "uvx"
        Write-Host "  [WARN] uvx not found in PATH; defaulting command to 'uvx'"
    }
}

Write-Host "`n=== [5/6] Updating Global MCP Configs (obsidian, blender & illustrator) ==="
$IllustratorMcpScript = Join-Path $WorkspaceRoot ".agents\mcp\illustrator-mcp\server.js"
$BlenderMcpExe = Join-Path $env:USERPROFILE ".local\bin\blender-mcp.exe"
$McpConfigPaths = @(
    (Join-Path $env:USERPROFILE ".gemini\config\mcp_config.json"),
    (Join-Path $env:USERPROFILE ".gemini\antigravity\mcp_config.json"),
    (Join-Path $env:USERPROFILE ".gemini\antigravity-obsidian\mcp_config.json")
)

foreach ($cfgPath in $McpConfigPaths) {
    $cfgDir = Split-Path -Parent $cfgPath
    if (-not (Test-Path $cfgDir)) {
        New-Item -ItemType Directory -Path $cfgDir -Force | Out-Null
    }
    if (Test-Path $cfgPath) {
        $json = Get-Content -Path $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } else {
        $json = [PSCustomObject]@{ mcpServers = [PSCustomObject]@{} }
    }
    if (-not $json.mcpServers) {
        $json | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value ([PSCustomObject]@{}) -Force
    }

    $obsidianEntry = [PSCustomObject]@{
        command = "node"
        args    = @($McpVaultScript, $ObsidianVaultPath)
    }
    $json.mcpServers | Add-Member -MemberType NoteProperty -Name "obsidian" -Value $obsidianEntry -Force

    # Preserve existing blender-mcp.exe configuration if already configured or if blender-mcp.exe exists
    $existingBlender = $json.mcpServers.PSObject.Properties["blender"]
    if ($existingBlender -and $existingBlender.Value.command -and ($existingBlender.Value.command -match "blender-mcp\.exe")) {
        Write-Host "  [OK] Preserved existing blender-mcp.exe config in $cfgPath"
    } elseif (Test-Path $BlenderMcpExe) {
        $blenderEntry = [PSCustomObject]@{
            command = $BlenderMcpExe
            args    = @()
            env     = [PSCustomObject]@{
                BLENDER_PATH     = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
                BLENDER_MCP_HOST = "localhost"
                BLENDER_MCP_PORT = "9876"
            }
        }
        $json.mcpServers | Add-Member -MemberType NoteProperty -Name "blender" -Value $blenderEntry -Force
    } else {
        $blenderEntry = [PSCustomObject]@{
            command = $UvxPath
            args    = @("mcp-for-blender")
        }
        $json.mcpServers | Add-Member -MemberType NoteProperty -Name "blender" -Value $blenderEntry -Force
    }

    $notebookLmEntry = [PSCustomObject]@{
        command = "node"
        args    = @($NotebookLmMcpScript)
    }
    $json.mcpServers | Add-Member -MemberType NoteProperty -Name "notebooklm-research" -Value $notebookLmEntry -Force

    $illustratorEntry = [PSCustomObject]@{
        command = "node"
        args    = @($IllustratorMcpScript)
    }
    $json.mcpServers | Add-Member -MemberType NoteProperty -Name "illustrator" -Value $illustratorEntry -Force

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($cfgPath, ($json | ConvertTo-Json -Depth 10), $utf8NoBom)
    Write-Host "  [OK] Updated MCP config: $cfgPath"
}

Write-Host "`n=== [6/6] Checking NotebookLM Auth Directory ==="
$NotebookLmStateDir = Join-Path $env:LOCALAPPDATA "notebooklm-mcp\Data\browser_state"
if (-not (Test-Path $NotebookLmStateDir)) {
    New-Item -ItemType Directory -Path $NotebookLmStateDir -Force | Out-Null
}
$NotebookLmStateFile = Join-Path $NotebookLmStateDir "state.json"
if (Test-Path $NotebookLmStateFile) {
    Write-Host "  [OK] NotebookLM state.json exists ($NotebookLmStateFile)"
} else {
    Write-Host "  [INFO] NotebookLM state.json not found on this PC yet (run setup_auth when needed)"
}

Write-Host "`n=== PC Environment Sync Complete ==="
