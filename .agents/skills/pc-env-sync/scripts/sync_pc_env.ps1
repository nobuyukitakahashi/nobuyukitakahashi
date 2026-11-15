param(
    [string]$WorkspaceRoot = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$CandidatePaths = @(
    "$env:LOCALAPPDATA\Programs\nodejs",
    "$env:ProgramFiles\nodejs",
    "$env:APPDATA\npm",
    "$env:LOCALAPPDATA\Programs\Git\cmd",
    "$env:ProgramFiles\Git\cmd",
    "$env:USERPROFILE\.local\bin",
    "$env:LOCALAPPDATA\Microsoft\WinGet\Links"
) | Where-Object { $_ -and (Test-Path $_) }
if ($CandidatePaths.Count -gt 0) {
    $env:PATH = ($CandidatePaths -join ";") + ";" + $env:PATH
}

function Test-AgyWorkspace {
    param([string]$PathToCheck)
    if ([string]::IsNullOrWhiteSpace($PathToCheck)) { return $false }
    if (-not (Test-Path $PathToCheck)) { return $false }
    $skillFile = Join-Path $PathToCheck ".agents\skills\pc-env-sync\SKILL.md"
    return (Test-Path $skillFile)
}

function Resolve-AgyWorkspaceRoot {
    param([string]$ExplicitPath, [string]$ScriptDirectory)

    if ($ExplicitPath -and (Test-AgyWorkspace $ExplicitPath)) {
        return (Resolve-Path $ExplicitPath).Path
    }
    if ($env:AGY_WORKSPACE_ROOT -and (Test-AgyWorkspace $env:AGY_WORKSPACE_ROOT)) {
        return (Resolve-Path $env:AGY_WORKSPACE_ROOT).Path
    }

    # 1) Relative to script location (when invoked inside repository)
    $scriptCandidate = Join-Path $ScriptDirectory "..\..\..\.."
    if (Test-Path $scriptCandidate) {
        $resolvedScriptCandidate = (Resolve-Path $scriptCandidate).Path
        if ((Test-AgyWorkspace $resolvedScriptCandidate) -and (Test-Path (Join-Path $resolvedScriptCandidate ".git"))) {
            return $resolvedScriptCandidate
        }
    }

    # 2) Walk up from current working directory
    $cur = (Get-Location).Path
    while ($cur) {
        if (Test-AgyWorkspace $cur) {
            return (Resolve-Path $cur).Path
        }
        $parent = Split-Path -Parent $cur
        if (-not $parent -or $parent -eq $cur) { break }
        $cur = $parent
    }

    # 3) Extract from existing mcp_config.json entries
    $existingConfigs = @(
        (Join-Path $env:USERPROFILE ".gemini\antigravity\mcp_config.json"),
        (Join-Path $env:USERPROFILE ".gemini\config\mcp_config.json")
    )
    foreach ($cfg in $existingConfigs) {
        if (Test-Path $cfg) {
            try {
                $cfgJson = Get-Content -Path $cfg -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($cfgJson -and $cfgJson.mcpServers) {
                    foreach ($prop in $cfgJson.mcpServers.PSObject.Properties) {
                        $argsList = $prop.Value.args
                        if ($argsList) {
                            foreach ($a in $argsList) {
                                if ($a -is [string] -and $a -match '^(.+?)[\\/]\.agents[\\/]mcp[\\/]') {
                                    $extracted = $Matches[1]
                                    if (Test-AgyWorkspace $extracted) {
                                        return (Resolve-Path $extracted).Path
                                    }
                                }
                            }
                        }
                    }
                }
            } catch {
                # Ignore malformed JSON during discovery
            }
        }
    }

    # 4) Scan ready drives (root, 1st-level subdirs like My Drive / localized drive folders) and USERPROFILE
    $searchBases = New-Object System.Collections.Generic.List[string]
    if ($env:USERPROFILE -and (Test-Path $env:USERPROFILE)) {
        $searchBases.Add($env:USERPROFILE)
    }
    $readyDrives = [System.IO.DriveInfo]::GetDrives() | Where-Object {
        $_.IsReady -and $_.DriveType -in @("Fixed", "Network", "Removable")
    }
    foreach ($drv in $readyDrives) {
        $searchBases.Add($drv.RootDirectory.FullName)
    }

    foreach ($base in $searchBases) {
        $directCandidates = @(
            (Join-Path $base "git\nobuyukitakahashi"),
            (Join-Path $base "nobuyukitakahashi")
        )
        foreach ($cand in $directCandidates) {
            if (Test-AgyWorkspace $cand) {
                return (Resolve-Path $cand).Path
            }
        }
        try {
            $firstLevelDirs = Get-ChildItem -Path $base -Directory -ErrorAction SilentlyContinue
            foreach ($dir in $firstLevelDirs) {
                $subCandidates = @(
                    (Join-Path $dir.FullName "git\nobuyukitakahashi"),
                    (Join-Path $dir.FullName "nobuyukitakahashi")
                )
                foreach ($cand in $subCandidates) {
                    if (Test-AgyWorkspace $cand) {
                        return (Resolve-Path $cand).Path
                    }
                }
            }
        } catch {
            # Ignore permission errors on system directories
        }
    }

    throw "Could not locate 'nobuyukitakahashi' workspace. Pass -WorkspaceRoot <path> or run inside the repository."
}

function Resolve-ObsidianVaultPath {
    param([string]$DriveRootPath)

    $candidates = @(
        (Join-Path $DriveRootPath "obsidian"),
        (Join-Path $DriveRootPath "obsidian\nobuyukitakahashi\nobuyukitakahashi")
    )
    foreach ($cand in $candidates) {
        if (Test-Path (Join-Path $cand ".obsidian")) {
            return (Resolve-Path $cand).Path
        }
    }

    # Check existing mcp_config.json for a valid vault path
    $existingConfigs = @(
        (Join-Path $env:USERPROFILE ".gemini\antigravity\mcp_config.json"),
        (Join-Path $env:USERPROFILE ".gemini\config\mcp_config.json")
    )
    foreach ($cfg in $existingConfigs) {
        if (Test-Path $cfg) {
            try {
                $cfgJson = Get-Content -Path $cfg -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($cfgJson -and $cfgJson.mcpServers -and $cfgJson.mcpServers.obsidian -and $cfgJson.mcpServers.obsidian.args.Count -ge 2) {
                    $existingVault = $cfgJson.mcpServers.obsidian.args[1]
                    if ($existingVault -and (Test-Path (Join-Path $existingVault ".obsidian"))) {
                        return (Resolve-Path $existingVault).Path
                    }
                }
            } catch {
                # Ignore malformed JSON
            }
        }
    }

    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            return (Resolve-Path $cand).Path
        }
    }
    return $candidates[0]
}

Write-Host "=== [1/6] Detecting Workspace, Tools & Google Drive Paths ==="
foreach ($requiredCmd in @("git", "node", "npm")) {
    if (-not (Get-Command $requiredCmd -ErrorAction SilentlyContinue)) {
        throw "Required command '$requiredCmd' was not found in PATH. Please install it first."
    }
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Resolve-AgyWorkspaceRoot -ExplicitPath $WorkspaceRoot -ScriptDirectory $ScriptDir
$DriveRoot = Split-Path -Parent (Split-Path -Parent $WorkspaceRoot)
$ObsidianVaultPath = Resolve-ObsidianVaultPath -DriveRootPath $DriveRoot

Write-Host "  Workspace : $WorkspaceRoot"
Write-Host "  DriveRoot : $DriveRoot"
Write-Host "  VaultPath : $ObsidianVaultPath"
if (-not (Test-Path (Join-Path $ObsidianVaultPath ".obsidian"))) {
    Write-Host "  [WARN] .obsidian directory not found at VaultPath yet (Google Drive sync may still be in progress)"
}

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
$DefaultSshKey = Join-Path $SshDir "id_ed25519"
if (-not (Test-Path $DefaultSshKey)) {
    Write-Host "  [INFO] ~/.ssh/id_ed25519 not found on this PC (copy your SSH private keys if SSH/Git SSH is needed)"
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
    "adobe-premiere",
    "adobe-aftereffects",
    "blender",
    "illustrator",
    "photoshop",
    "premiere",
    "aftereffects",
    "davinci",
    "pano2vr",
    "krpano",
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
$GlobalMasterPluginSrc = Join-Path $WorkspaceRoot ".agents\plugins\global-master-rules"
if (Test-Path $GlobalMasterPluginSrc) {
    Copy-Item -Path $GlobalMasterPluginSrc -Destination $GlobalPluginsDir -Recurse -Force
    Write-Host "  [OK] Synced global plugin: global-master-rules"
    $MasterRulesMd = Join-Path $GlobalMasterPluginSrc "rules\AGENTS.md"
    if (Test-Path $MasterRulesMd) {
        $GlobalConfigDir = Join-Path $env:USERPROFILE ".gemini\config"
        $GlobalRulesDir = Join-Path $GlobalConfigDir "rules"
        if (-not (Test-Path $GlobalRulesDir)) {
            New-Item -ItemType Directory -Path $GlobalRulesDir -Force | Out-Null
        }
        Copy-Item -Path $MasterRulesMd -Destination (Join-Path $GlobalConfigDir "AGENTS.md") -Force
        Copy-Item -Path $MasterRulesMd -Destination (Join-Path $GlobalRulesDir "AGENTS.md") -Force
        Write-Host "  [OK] Synced account-wide master rules: ~/.gemini/config/AGENTS.md & ~/.gemini/config/rules/AGENTS.md"
    }
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

Write-Host "`n=== [5/6] Updating Global MCP Configs (obsidian, blender, illustrator, photoshop, premiere & aftereffects) ==="
$NodeCmd = Get-Command node -ErrorAction SilentlyContinue
$NodeExe = if ($NodeCmd) { $NodeCmd.Source } else { "node" }
$IllustratorMcpScript = Join-Path $WorkspaceRoot ".agents\mcp\illustrator-mcp\server.js"
$PhotoshopMcpScript = Join-Path $WorkspaceRoot ".agents\mcp\photoshop-mcp\server.js"
$PremiereMcpScript = Join-Path $WorkspaceRoot ".agents\mcp\premiere-mcp\server.js"
$AfterEffectsMcpScript = Join-Path $WorkspaceRoot ".agents\mcp\aftereffects-mcp\server.js"
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
        $rawCfg = Get-Content -Path $cfgPath -Raw -Encoding UTF8
        if ($rawCfg -and $rawCfg.Trim()) {
            $json = $rawCfg | ConvertFrom-Json
        } else {
            $json = $null
        }
    } else {
        $json = $null
    }
    if (-not $json) {
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

    $DetectedBlenderExe = @("C:\Program Files\Blender Foundation", "$env:LOCALAPPDATA\Programs\Blender Foundation") |
        Where-Object { Test-Path $_ } |
        ForEach-Object { Get-ChildItem $_ -Recurse -Filter "blender.exe" -ErrorAction SilentlyContinue } |
        Sort-Object FullName -Descending |
        Select-Object -First 1 -ExpandProperty FullName
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

    $premiereEntry = [PSCustomObject]@{
        command = $NodeExe
        args    = @($PremiereMcpScript)
    }
    $json.mcpServers | Add-Member -MemberType NoteProperty -Name "premiere" -Value $premiereEntry -Force

    $afterEffectsEntry = [PSCustomObject]@{
        command = $NodeExe
        args    = @($AfterEffectsMcpScript)
    }
    $json.mcpServers | Add-Member -MemberType NoteProperty -Name "aftereffects" -Value $afterEffectsEntry -Force

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

Write-Host "`n=== PC Environment Sync Complete (Reload Antigravity if MCP config was updated) ==="
