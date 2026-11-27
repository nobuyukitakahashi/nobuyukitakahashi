#!/usr/bin/env python3
"""
Fast Win32 Moho 14.5.1 wake-up nudger (ctypes, stdlib only, ~40ms startup).
Stage 1 (0..450ms): Silent RedrawWindow + InvalidateRect + WM_MOUSEMOVE
Stage 2 (450..750ms): + SendMessageTimeout(WM_ACTIVATEAPP / WM_ACTIVATE)
Stage 3 (750ms+): Micro focus-pulse fallback that wakes idle/minimized Moho
                  and immediately restores previous foreground window.
"""

import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import tempfile
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

ENUM_PROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

user32.EnumWindows.argtypes = [ENUM_PROC, wt.LPARAM]
user32.EnumChildWindows.argtypes = [wt.HWND, ENUM_PROC, wt.LPARAM]
user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
user32.IsWindowVisible.argtypes = [wt.HWND]
user32.IsIconic.argtypes = [wt.HWND]
user32.RedrawWindow.argtypes = [wt.HWND, wt.LPVOID, wt.LPVOID, wt.UINT]
user32.InvalidateRect.argtypes = [wt.HWND, wt.LPVOID, wt.BOOL]
user32.UpdateWindow.argtypes = [wt.HWND]
user32.PostMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
user32.SendMessageTimeoutW.argtypes = [
    wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM, wt.UINT, wt.UINT, ctypes.POINTER(wt.LPARAM)
]
user32.GetForegroundWindow.restype = wt.HWND
user32.GetShellWindow.restype = wt.HWND
user32.SetForegroundWindow.argtypes = [wt.HWND]
user32.BringWindowToTop.argtypes = [wt.HWND]
user32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
user32.AttachThreadInput.argtypes = [wt.DWORD, wt.DWORD, wt.BOOL]
user32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
user32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
user32.GetClientRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
user32.keybd_event.argtypes = [wt.BYTE, wt.BYTE, wt.DWORD, wt.WPARAM]
kernel32.GetCurrentThreadId.restype = wt.DWORD

RDW_INVALIDATE = 0x0001
RDW_INTERNALPAINT = 0x0002
RDW_ALLCHILDREN = 0x0080
RDW_UPDATENOW = 0x0100
WM_ACTIVATE = 0x0006
WM_SETFOCUS = 0x0007
WM_PAINT = 0x000F
WM_ACTIVATEAPP = 0x001C
WM_MOUSEMOVE = 0x0200
WM_NCHITTEST = 0x0084
WM_SETCURSOR = 0x0020
SMTO_ABORTIFHUNG = 0x0002
SW_SHOW = 5
SW_RESTORE = 9
VK_MENU = 0x12
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002


def get_moho_pids():
    pids = set()
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq Moho.exe", "/FO", "CSV", "/NH"],
            creationflags=0x08000000,
            text=True,
            timeout=2,
        )
        for line in out.splitlines():
            if "moho.exe" in line.lower():
                parts = [p.strip('"') for p in line.split('","')]
                if len(parts) > 1 and parts[1].isdigit():
                    pids.add(int(parts[1]))
    except Exception:
        pass
    return pids


def get_window_text(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, buf, 256)
    return buf.value


def get_class_name(hwnd):
    buf = ctypes.create_unicode_buffer(128)
    user32.GetClassNameW(hwnd, buf, 128)
    return buf.value


def is_moho_app_window(hwnd):
    cls = get_class_name(hwnd)
    if cls in ("IME", "MSCTFIME UI", "CicMarshalWndClass"):
        return False
    if cls == "LM_Wnd":
        return True
    if user32.IsWindowVisible(hwnd):
        return True
    title = get_window_text(hwnd)
    return "Moho" in title


def find_moho_top_windows(pids, include_hidden=False):
    found = []
    stats = {"total": 0, "pid_all": 0, "pid_vis": 0}

    def cb(hwnd, lparam):
        stats["total"] += 1
        wpid = wt.DWORD(0)
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value in pids:
            stats["pid_all"] += 1
            vis = bool(user32.IsWindowVisible(hwnd))
            if vis:
                stats["pid_vis"] += 1
            if include_hidden or is_moho_app_window(hwnd):
                found.append(hwnd)
        return True

    user32.EnumWindows(ENUM_PROC(cb), 0)
    return found, stats


def enum_children(hwnd):
    children = []

    def cb(ch, lparam):
        children.append(ch)
        return True

    user32.EnumChildWindows(hwnd, ENUM_PROC(cb), 0)
    return children


def describe_windows(pids):
    tops, stats = find_moho_top_windows(pids, include_hidden=True)
    parts = [f"STATS(total={stats['total']},pid_all={stats['pid_all']},pid_vis={stats['pid_vis']})"]
    for h in tops:
        cc = len(enum_children(h))
        parts.append(
            f"HWND={h} Vis={bool(user32.IsWindowVisible(h))} Min={bool(user32.IsIconic(h))} Children={cc} "
            f"Class={get_class_name(h)} Title={get_window_text(h)}"
        )
    return " | ".join(parts)


def center_lparam(hwnd, tick):
    rc = wt.RECT()
    if user32.GetClientRect(hwnd, ctypes.byref(rc)) and rc.right > 40 and rc.bottom > 40:
        cx = (rc.right // 2) + (2 if (tick % 2 == 0) else -2)
        cy = (rc.bottom // 2) + (1 if (tick % 2 == 0) else -1)
        return ((cy & 0xFFFF) << 16) | (cx & 0xFFFF)
    return 0x01900190 if (tick % 2 == 0) else 0x01920192


def nudge_silent(pids, tick, send_activate):
    tops, _ = find_moho_top_windows(pids, include_hidden=False)
    flags = RDW_INVALIDATE | RDW_INTERNALPAINT | RDW_ALLCHILDREN | RDW_UPDATENOW
    for h in tops:
        xy = center_lparam(h, tick)
        if send_activate:
            res = wt.LPARAM(0)
            user32.SendMessageTimeoutW(h, WM_ACTIVATEAPP, 1, 0, SMTO_ABORTIFHUNG, 60, ctypes.byref(res))
            user32.SendMessageTimeoutW(h, WM_ACTIVATE, 1, 0, SMTO_ABORTIFHUNG, 60, ctypes.byref(res))
            user32.PostMessageW(h, WM_SETFOCUS, 0, 0)
        user32.PostMessageW(h, WM_MOUSEMOVE, 0, xy)
        user32.PostMessageW(h, WM_SETCURSOR, h, (WM_MOUSEMOVE << 16) | 1)
        user32.InvalidateRect(h, None, False)
        user32.RedrawWindow(h, None, None, flags)
        user32.PostMessageW(h, WM_PAINT, 0, 0)
        user32.UpdateWindow(h)
        for ch in enum_children(h):
            cxy = center_lparam(ch, tick)
            user32.PostMessageW(ch, WM_MOUSEMOVE, 0, cxy)
            user32.InvalidateRect(ch, None, False)
            user32.RedrawWindow(ch, None, None, flags)
            user32.PostMessageW(ch, WM_PAINT, 0, 0)
    return len(tops)


def pick_primary_window(pids):
    best = 0
    best_score = -1
    tops, _ = find_moho_top_windows(pids, include_hidden=False)
    for h in tops:
        cc = len(enum_children(h))
        title = get_window_text(h)
        score = cc + (50 if "Moho" in title else 0) + (100 if ".moho" in title else 0)
        if score > best_score:
            best_score = score
            best = h
    return best


def activate_moho(hwnd):
    if not hwnd:
        return 0
    prev_fg = user32.GetForegroundWindow()
    user32.ShowWindow(hwnd, SW_RESTORE if user32.IsIconic(hwnd) else SW_SHOW)

    dummy = wt.DWORD(0)
    fg_tid = user32.GetWindowThreadProcessId(prev_fg, ctypes.byref(dummy)) if prev_fg else 0
    target_tid = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(dummy))
    cur_tid = kernel32.GetCurrentThreadId()

    if fg_tid and fg_tid != cur_tid:
        user32.AttachThreadInput(cur_tid, fg_tid, True)
    if target_tid and target_tid != cur_tid:
        user32.AttachThreadInput(cur_tid, target_tid, True)

    # Standard Win32 Alt tap to allow foreground switch
    user32.keybd_event(VK_MENU, 0x45, KEYEVENTF_EXTENDEDKEY, 0)
    user32.keybd_event(VK_MENU, 0x45, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)

    if prev_fg == hwnd:
        shell = user32.GetShellWindow()
        if shell and shell != hwnd:
            user32.SetForegroundWindow(shell)
            time.sleep(0.04)

    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)

    if target_tid and target_tid != cur_tid:
        user32.AttachThreadInput(cur_tid, target_tid, False)
    if fg_tid and fg_tid != cur_tid:
        user32.AttachThreadInput(cur_tid, fg_tid, False)
    return prev_fg


def restore_foreground(prev_fg, moho_hwnd):
    if not prev_fg or prev_fg == moho_hwnd:
        return
    dummy = wt.DWORD(0)
    cur_fg = user32.GetForegroundWindow()
    fg_tid = user32.GetWindowThreadProcessId(cur_fg, ctypes.byref(dummy)) if cur_fg else 0
    prev_tid = user32.GetWindowThreadProcessId(prev_fg, ctypes.byref(dummy))
    cur_tid = kernel32.GetCurrentThreadId()
    if fg_tid and fg_tid != cur_tid:
        user32.AttachThreadInput(cur_tid, fg_tid, True)
    if prev_tid and prev_tid != cur_tid:
        user32.AttachThreadInput(cur_tid, prev_tid, True)
    user32.SetForegroundWindow(prev_fg)
    if prev_tid and prev_tid != cur_tid:
        user32.AttachThreadInput(cur_tid, prev_tid, False)
    if fg_tid and fg_tid != cur_tid:
        user32.AttachThreadInput(cur_tid, fg_tid, False)


def main():
    res_file = ""
    timeout_ms = 15000
    single_shot = False
    diagnostics = False
    allow_focus = True

    i = 1
    while i < len(sys.argv):
        a = sys.argv[i].lower()
        if a in ("-resfile", "--res") and i + 1 < len(sys.argv):
            res_file = sys.argv[i + 1]
            i += 2
        elif a in ("-timeoutms", "--timeout") and i + 1 < len(sys.argv):
            timeout_ms = int(sys.argv[i + 1])
            i += 2
        elif a in ("-singleshot", "--single"):
            single_shot = True
            i += 1
        elif a in ("-diagnostics", "--diag"):
            diagnostics = True
            i += 1
        elif a == "-nofocus":
            allow_focus = False
            i += 1
        else:
            i += 1

    pids = get_moho_pids()
    if not pids:
        print("NO_PROCESS")
        return 0
    if diagnostics:
        print(describe_windows(pids))
        return 0
    if single_shot:
        print(f"NUDGED={nudge_silent(pids, 0, True)}")
        return 0

    debug_enabled = os.environ.get("MOHO_BRIDGE_DEBUG") == "1"
    trace_path = os.path.join(tempfile.gettempdir(), "agy-moho-bridge", "nudge_last.log")

    def trace(msg):
        if not debug_enabled:
            return
        try:
            os.makedirs(os.path.dirname(trace_path), exist_ok=True)
            with open(trace_path, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
        except Exception:
            pass

    if debug_enabled:
        try:
            os.makedirs(os.path.dirname(trace_path), exist_ok=True)
            with open(trace_path, "w", encoding="utf-8") as f:
                f.write(f"START pids={sorted(pids)} res={res_file}\n")
        except Exception:
            pass
    trace("WINDOWS: " + describe_windows(pids))

    t0 = time.monotonic()
    tick = 0
    did_focus = False
    prev_fg = 0
    moho_hwnd = 0

    try:
        while (time.monotonic() - t0) * 1000 < timeout_ms:
            if res_file and os.path.exists(res_file):
                trace(f"RES_FOUND at {int((time.monotonic()-t0)*1000)}ms tick={tick}")
                break
            elapsed = (time.monotonic() - t0) * 1000
            cnt = nudge_silent(pids, tick, elapsed >= 400)
            if tick == 0:
                trace(f"TICK0 NudgeSilent={cnt}")

            if allow_focus and (not did_focus) and elapsed >= 700:
                did_focus = True
                moho_hwnd = pick_primary_window(pids)
                trace(f"STAGE3 pick={moho_hwnd}")
                if moho_hwnd:
                    prev_fg = activate_moho(moho_hwnd)
                    trace(f"STAGE3 prevFg={prev_fg} nowFg={user32.GetForegroundWindow()}")
                    p0 = time.monotonic()
                    while (time.monotonic() - p0) * 1000 < 600:
                        if res_file and os.path.exists(res_file):
                            trace(f"STAGE3 RES_FOUND at {int((time.monotonic()-t0)*1000)}ms")
                            break
                        nudge_silent(pids, tick, False)
                        time.sleep(0.03)
                        tick += 1
                    restore_foreground(prev_fg, moho_hwnd)
                    prev_fg = 0

            tick += 1
            time.sleep(0.06)
    finally:
        if prev_fg and moho_hwnd:
            restore_foreground(prev_fg, moho_hwnd)

    return 0


if __name__ == "__main__":
    sys.exit(main())
