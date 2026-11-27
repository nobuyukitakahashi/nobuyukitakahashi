"use strict";

/**
 * Win32 / macOS Moho window helper & 3-stage wake-up nudger.
 * Uses standalone `nudge-moho.ps1` (pure C# Win32 bindings) so:
 *   Stage 1 (0..600ms): 100% silent RedrawWindow + InvalidateRect + WM_MOUSEMOVE
 *   Stage 2 (600..1200ms): + non-focus-stealing SendMessageTimeout(WM_ACTIVATEAPP/WM_ACTIVATE)
 *   Stage 3 (1200ms+): automatic micro focus-pulse fallback that wakes idle/minimized Moho
 *                      and restores previous foreground window immediately once response arrives.
 */

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync, spawn } = require("child_process");
const { IS_WIN, IS_MAC, detectMohoEnvironment } = require("./env");

const PS_EXE = IS_WIN && process.env.SystemRoot
  ? path.join(process.env.SystemRoot, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
  : "powershell.exe";

const NUDGE_PY = path.join(__dirname, "nudge_moho.py");
const NUDGE_PS1 = path.join(__dirname, "nudge-moho.ps1");

function resolvePythonExe() {
  if (!IS_WIN) return "python3";
  const cands = [
    process.env.PYTHON_PATH,
    path.join(os.homedir(), "AppData", "Local", "Python", "bin", "python.exe"),
    path.join(os.homedir(), "AppData", "Local", "Microsoft", "WindowsApps", "python.exe")
  ].filter(Boolean);
  for (const c of cands) {
    if (fs.existsSync(c)) return c;
  }
  return "python";
}

/**
 * Send a single-shot silent repaint/update nudge (or return window diagnostics).
 */
function nudgeMohoWindow(options = {}) {
  if (IS_WIN) {
    try {
      const usePy = fs.existsSync(NUDGE_PY);
      const cmd = usePy ? resolvePythonExe() : PS_EXE;
      const args = usePy
        ? [NUDGE_PY, options.diagnostics ? "-diagnostics" : "-singleshot"]
        : [
            "-NonInteractive",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            NUDGE_PS1,
            options.diagnostics ? "-Diagnostics" : "-SingleShot"
          ];
      const res = spawnSync(cmd, args, {
        encoding: "utf8",
        timeout: 6000,
        windowsHide: true
      });
      const out = (res.stdout || "").trim();
      if (res.error || res.status !== 0) {
        return {
          ok: false,
          nudgedWindows: 0,
          error: res.error ? res.error.message : (res.stderr || `Nudger exited ${res.status}`).trim(),
          raw: out
        };
      }
      if (options.diagnostics) {
        return { ok: true, windows: out };
      }
      const m = out.match(/NUDGED=(\d+)/);
      return { ok: true, nudgedWindows: m ? parseInt(m[1], 10) : 0, raw: out };
    } catch (err) {
      return { ok: false, error: err.message };
    }
  } else if (IS_MAC) {
    try {
      spawnSync(
        "osascript",
        ["-e", 'tell application "System Events" to if exists process "Moho" then perform action "AXRaise" of front window of process "Moho"'],
        { timeout: 3000 }
      );
      return { ok: true, nudgedWindows: 1 };
    } catch (err) {
      return { ok: false, error: err.message };
    }
  }
  return { ok: false, error: "Unsupported platform" };
}

/**
 * Spawn a single fast background PowerShell nudger that compiles C# Win32 bindings ONCE
 * and drives the 3-stage wake-up loop until resPath appears or timeoutMs elapses.
 */
function startNudgeLoop(resPath, timeoutMs = 15000) {
  if (!IS_WIN) return null;
  try {
    const usePy = fs.existsSync(NUDGE_PY);
    const cmd = usePy ? resolvePythonExe() : PS_EXE;
    const args = usePy
      ? [NUDGE_PY, "-resfile", String(resPath || ""), "-timeoutms", String(timeoutMs)]
      : [
          "-NonInteractive",
          "-NoProfile",
          "-ExecutionPolicy",
          "Bypass",
          "-File",
          NUDGE_PS1,
          "-ResFile",
          String(resPath || ""),
          "-TimeoutMs",
          String(timeoutMs)
        ];
    const child = spawn(cmd, args, { stdio: "ignore", windowsHide: true });
    child.unref();
    return child;
  } catch (_) {
    return null;
  }
}

/**
 * Launch Moho Pro GUI (optionally opening a specific .moho file).
 */
function launchMohoGui(mohoFilePath = null) {
  const env = detectMohoEnvironment();
  if (!env.installed || !env.mohoExe) {
    return { ok: false, error: "Moho 14 executable not found" };
  }
  const args = mohoFilePath ? [path.resolve(mohoFilePath)] : [];
  const child = spawn(env.mohoExe, args, {
    detached: true,
    stdio: "ignore",
    windowsHide: false
  });
  child.unref();
  return {
    ok: true,
    pid: child.pid,
    mohoExe: env.mohoExe,
    openedFile: mohoFilePath ? path.resolve(mohoFilePath) : null
  };
}

/**
 * Send Ctrl+Shift+Alt+L (Reload Tools and Brushes) to Moho window on Windows.
 */
function triggerReloadScriptsWindows() {
  if (!IS_WIN) return { ok: false, error: "Reload shortcut helper only implemented on Windows" };
  const ps = `
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class AgyFocus {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@
$p = Get-Process -Name "Moho" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Write-Output "NO_VISIBLE_WINDOW"; exit 0 }
[AgyFocus]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
[AgyFocus]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 250
[System.Windows.Forms.SendKeys]::SendWait("^+%l")
Write-Output "RELOAD_SENT"
`;
  const res = spawnSync(
    PS_EXE,
    ["-NonInteractive", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
    { encoding: "utf8", timeout: 5000, windowsHide: true }
  );
  const out = (res.stdout || "").trim();
  return { ok: out.includes("RELOAD_SENT"), status: out };
}

module.exports = {
  nudgeMohoWindow,
  startNudgeLoop,
  launchMohoGui,
  triggerReloadScriptsWindows
};
