$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PATH = "$env:LOCALAPPDATA\Programs\nodejs;$env:USERPROFILE\.local\bin;$env:LOCALAPPDATA\Microsoft\WinGet\Links;$env:PATH"

Write-Host "=== [1/6] Detecting Workspace & Google Drive Paths ==="
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = (Resolve-Path (Join-Path $ScriptDir "..\..\..\..")).Path
$DriveRoot = Split-Path -Parent (Split-Path -Parent $WorkspaceRoot)
$ObsidianVaultPath = Join-Path $DriveRoot "obsidian\nobuyukitakahashi\nobuyukitakahashi"

Write-Host "  Workspace : $WorkspaceRoot"
Write-Host "  DriveRoot : $DriveRoot"
Write-Host "  VaultPath : $ObsidianVaultPath"

Write-Host "`n=== [1.5/6] Ensuring Git Global Config, ~/.ssh/config & Local Bin PATH ==="
$NpmRoamingDir = Join-Path $env:APPDATA "npm"
if (-not (Test-Path $NpmRoamingDir)) {
    New-Item -ItemType Directory -Path $NpmRoamingDir -Force | Out-Null
}
$LocalBinDir = Join-Path $env:USERPROFILE ".local\bin"
if (-not (Test-Path $LocalBinDir)) {
    New-Item -ItemType Directory -Path $LocalBinDir -Force | Out-Null
}
$CurrentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($CurrentUserPath -notlike "*$LocalBinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$LocalBinDir;$CurrentUserPath", "User")
}

git config --global user.name "nobuyukitakahashi"
git config --global user.email "nobuyukitakahashi@outlook.com"
git config --global core.quotepath false
git config --global core.autocrlf false
git config --global init.defaultBranch main
git config --global --replace-all safe.directory "*"
Write-Host "  [OK] Configured ~/.gitconfig (user.name, user.email, safe.directory)"

$SshDir = Join-Path $env:USERPROFILE ".ssh"
if (-not (Test-Path $SshDir)) {
    New-Item -ItemType Directory -Path $SshDir -Force | Out-Null
}
$SshConfigPath = Join-Path $SshDir "config"
if (-not (Test-Path $SshConfigPath)) {
    $DefaultSshConfig = @"
Host *
    ServerAliveInterval 60
    TCPKeepAlive yes
    StrictHostKeyChecking accept-new

Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519

Host ssh-hoshinomorijp.heteml.net heteml-stella heteml-shinshu
    HostName ssh-hoshinomorijp.heteml.net
    Port 2222
    User hoshinomori
    IdentityFile ~/.ssh/id_ed25519

Host ssh-ilcsupporters.heteml.net heteml-fit heteml-iidacable
    HostName ssh-ilcsupporters.heteml.net
    Port 2222
    User ilcsupporters
    IdentityFile ~/.ssh/id_ed25519

Host ssh-iidajob.heteml.net heteml-iidajob
    HostName ssh-iidajob.heteml.net
    Port 2222
    User iidajob
    IdentityFile ~/.ssh/id_ed25519

Host ssh-vill-tenryu.heteml.net heteml-shimoinakyoikukai
    HostName ssh-vill-tenryu.heteml.net
    Port 2222
    User vill-tenryu
    IdentityFile ~/.ssh/id_ed25519

Host ssh-iikou-d.heteml.net heteml-iikoud
    HostName ssh-iikou-d.heteml.net
    Port 2222
    User iikoud
    IdentityFile ~/.ssh/id_ed25519

Host xserver-kumashiro sv228.xbiz.ne.jp
    HostName sv228.xbiz.ne.jp
    User xb704395
    Port 10022
    IdentityFile ~/.ssh/id_rsa_kumashiro.key
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host xserver-iida-hs sv898.xbiz.ne.jp
    HostName sv898.xbiz.ne.jp
    User xb320696
    Port 10022
    IdentityFile ~/.ssh/id_rsa_iida_hs.key
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host xserver-takey sv256.xbiz.ne.jp
    HostName sv256.xbiz.ne.jp
    User xb499609
    Port 10022
    IdentityFile ~/.ssh/xb499609.key
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host coreserver-hiraya v2008.coreserver.jp
    HostName v2008.coreserver.jp
    Port 22
    User rvzmiulh
    IdentityFile ~/.ssh/id_rsa_coreserver
    IdentityFile ~/.ssh/id_rsa_coreserver_nopass
    IdentityFile ~/.ssh/id_ed25519_coreserver
    IdentityFile ~/.ssh/id_ed25519

Host coreserver-hinokigasa v2011.coreserver.jp
    HostName v2011.coreserver.jp
    Port 22
    User zhxahtdr
    IdentityFile ~/.ssh/hinokigasa_rsa
    IdentityFile ~/.ssh/id_rsa_coreserver
    IdentityFile ~/.ssh/id_rsa_coreserver_nopass
    IdentityFile ~/.ssh/id_ed25519_coreserver
    IdentityFile ~/.ssh/id_ed25519

Host sakura-beig beig.sakura.ne.jp
    HostName beig.sakura.ne.jp
    Port 22
    User beig
    IdentityFile ~/.ssh/id_ecdsa_sakura_decrypted
    IdentityFile ~/.ssh/id_ecdsa_sakura
    IdentityFile ~/.ssh/id_ed25519

Host lolipop-maezawa ssh.lolipop.jp
    HostName ssh.lolipop.jp
    Port 2222
    User main.jp-92260324ac787746
    IdentityFile ~/.ssh/id_ed25519
"@
    $utf8NoBomInit = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($SshConfigPath, $DefaultSshConfig, $utf8NoBomInit)
    Write-Host "  [OK] Created unified ~/.ssh/config ($SshConfigPath)"
} else {
    Write-Host "  [OK] ~/.ssh/config already present ($SshConfigPath)"
}

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
    "adobe-photoshop",
    "blender",
    "illustrator",
    "photoshop",
    "davinci",
    "writing",
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

Write-Host "`n=== [5/6] Updating Global MCP Configs (obsidian, blender, illustrator & photoshop) ==="
$NodeCmd = Get-Command node -ErrorAction SilentlyContinue
$NodeExe = if ($NodeCmd) { $NodeCmd.Source } else { "node" }
$IllustratorMcpScript = Join-Path $WorkspaceRoot ".agents\mcp\illustrator-mcp\server.js"
$PhotoshopMcpScript = Join-Path $WorkspaceRoot ".agents\mcp\photoshop-mcp\server.js"
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
        command = $NodeExe
        args    = @($McpVaultScript, $ObsidianVaultPath)
    }
    $json.mcpServers | Add-Member -MemberType NoteProperty -Name "obsidian" -Value $obsidianEntry -Force

    $DetectedBlenderExe = Get-ChildItem "C:\Program Files\Blender Foundation" -Recurse -Filter "blender.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
    if (-not $DetectedBlenderExe) {
        $DetectedBlenderExe = "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe"
    }

    # Preserve existing blender-mcp.exe configuration if already configured or if blender-mcp.exe exists
    $existingBlender = $json.mcpServers.PSObject.Properties["blender"]
    if (Test-Path $BlenderMcpExe) {
        $blenderEntry = [PSCustomObject]@{
            command = $BlenderMcpExe
            args    = @()
            env     = [PSCustomObject]@{
                BLENDER_PATH     = $DetectedBlenderExe
                BLENDER_MCP_HOST = "localhost"
                BLENDER_MCP_PORT = "9876"
            }
        }
        $json.mcpServers | Add-Member -MemberType NoteProperty -Name "blender" -Value $blenderEntry -Force
    } elseif ($existingBlender -and $existingBlender.Value.command -and ($existingBlender.Value.command -match "blender-mcp\.exe")) {
        Write-Host "  [OK] Preserved existing blender-mcp.exe config in $cfgPath"
    } else {
        $blenderEntry = [PSCustomObject]@{
            command = $UvxPath
            args    = @("mcp-for-blender")
        }
        $json.mcpServers | Add-Member -MemberType NoteProperty -Name "blender" -Value $blenderEntry -Force
    }

    $notebookLmEntry = [PSCustomObject]@{
        command = $NodeExe
        args    = @($NotebookLmMcpScript)
    }
    $json.mcpServers | Add-Member -MemberType NoteProperty -Name "notebooklm-research" -Value $notebookLmEntry -Force

    $illustratorEntry = [PSCustomObject]@{
        command = $NodeExe
        args    = @($IllustratorMcpScript)
    }
    $json.mcpServers | Add-Member -MemberType NoteProperty -Name "illustrator" -Value $illustratorEntry -Force

    $photoshopEntry = [PSCustomObject]@{
        command = $NodeExe
        args    = @($PhotoshopMcpScript)
    }
    $json.mcpServers | Add-Member -MemberType NoteProperty -Name "photoshop" -Value $photoshopEntry -Force

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
