#!/usr/bin/env python3
"""
全プロジェクト横断 健康診断スクリプト (07_QA_Dept)
G:/マイドライブ/git 配下（nobuyukitakahashi除く）＋ G:/マイドライブ/obsidian の
Git健全性・偽テンプレート・旧ツール名・BOM・参照ズレ・秘密情報追跡・SQL肥大化を一括監査する。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PRUNE_DIRS = {".git", "node_modules", ".venv", "venv", "env", "__pycache__", "vendor", "wp-includes", "wp-admin", ".obsidian"}
OLD_TOOLS_RE = re.compile(r"\b(write_to_file|replace_file_content|view_file|multi_replace_file_content)\b")
STALE_REF_RE = re.compile(r"(global-master-rules`?\s*§6|user_global`?\s*§3|user_global`?\s*§8)", re.I)
SECRET_NAME_RE = re.compile(r"(^\.env($|\.(?!example$|sample$|template$))|wp-config\.php$|\.(sql|sql\.gz|key|pem|ppk|wpress|bak|pfx)$)", re.I)


def run_git(cwd: Path, args: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(["git", "-C", str(cwd)] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


def audit_all(git_base: Path, obsidian_dir: Path) -> dict:
    projects: list[tuple[str, str, Path]] = []
    if git_base.exists():
        for grp in sorted(git_base.iterdir()):
            if not grp.is_dir() or grp.name == "nobuyukitakahashi":
                continue
            for sub in sorted(grp.iterdir()):
                if sub.is_dir():
                    projects.append((grp.name, sub.name, sub))
    if obsidian_dir.exists():
        projects.append(("obsidian", "obsidian", obsidian_dir))

    issues_critical: list[str] = []
    issues_warn: list[str] = []
    summary: list[dict] = []

    for grp, name, path in projects:
        label = f"{grp}/{name}"
        has_git = (path / ".git").exists()
        rec = {"project": label, "has_git": has_git, "dirty": 0, "issues": []}

        # Git health
        if has_git:
            rc, st, err = run_git(path, ["status", "--porcelain"])
            if rc != 0:
                msg = f"{label}: git status error ({err[:80]})"
                issues_critical.append(msg)
                rec["issues"].append(msg)
            else:
                lines = [l for l in st.splitlines() if l.strip()]
                rec["dirty"] = len(lines)
                if len(lines) > 50:
                    msg = f"{label}: excessive uncommitted changes ({len(lines)})"
                    issues_warn.append(msg)
                    rec["issues"].append(msg)
            rc2, tr, _ = run_git(path, ["ls-files"])
            if rc2 == 0:
                for l in tr.splitlines():
                    if SECRET_NAME_RE.search(os.path.basename(l)):
                        msg = f"{label}: tracked sensitive/backup file ({l})"
                        issues_critical.append(msg)
                        rec["issues"].append(msg)

        # Rules & legacy template checks
        am = path / "AGENTS.md"
        if am.exists():
            raw = am.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                msg = f"{label}: UTF-8 BOM in AGENTS.md"
                issues_critical.append(msg)
                rec["issues"].append(msg)
            if len(raw) > 24000:
                msg = f"{label}: AGENTS.md exceeds 24,000B ({len(raw)}B)"
                issues_critical.append(msg)
                rec["issues"].append(msg)
            txt = raw.decode("utf-8", errors="ignore")
            if "Framework: Streamlit" in txt and name != "your-project-template":
                msg = f"{label}: fake Streamlit template left in AGENTS.md"
                issues_critical.append(msg)
                rec["issues"].append(msg)
            if OLD_TOOLS_RE.search(txt):
                msg = f"{label}: deprecated tool names in AGENTS.md"
                issues_critical.append(msg)
                rec["issues"].append(msg)
            if STALE_REF_RE.search(txt):
                msg = f"{label}: stale rule section reference in AGENTS.md"
                issues_critical.append(msg)
                rec["issues"].append(msg)

        # Legacy 3 copied skills
        sk_dir = path / ".agents" / "skills"
        if sk_dir.exists():
            legacy = [d.name for d in sk_dir.iterdir() if d.is_dir() and d.name in ("loop-step", "plan", "review")]
            if legacy:
                msg = f"{label}: legacy duplicated skills {legacy}"
                issues_warn.append(msg)
                rec["issues"].append(msg)

        # Uncompressed SQL dumps
        sql_mb = 0.0
        sql_cnt = 0
        bkp = path / "backups"
        if bkp.exists():
            for f in bkp.rglob("*.sql"):
                try:
                    sql_mb += f.stat().st_size / 1048576
                    sql_cnt += 1
                except OSError:
                    pass
        if sql_cnt > 0:
            msg = f"{label}: {sql_cnt} uncompressed .sql backups ({round(sql_mb, 1)}MB)"
            issues_warn.append(msg)
            rec["issues"].append(msg)

        # Obsidian misplaced org dirs
        if grp == "obsidian":
            for bad_d in ("02_Creative_Dept", "04_Delivery_Dept"):
                if (path / bad_d).exists():
                    msg = f"{label}: misplaced org directory '{bad_d}'"
                    issues_critical.append(msg)
                    rec["issues"].append(msg)

        summary.append(rec)

    return {
        "status": "PASS" if not issues_critical else "FAIL",
        "audited_count": len(summary),
        "critical_count": len(issues_critical),
        "warning_count": len(issues_warn),
        "critical": issues_critical,
        "warnings": issues_warn,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-project health audit")
    parser.add_argument("--git-base", default=r"G:\マイドライブ\git")
    parser.add_argument("--obsidian", default=r"G:\マイドライブ\obsidian")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    res = audit_all(Path(args.git_base), Path(args.obsidian))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"STATUS: {res['status']} (audited={res['audited_count']}, critical={res['critical_count']}, warnings={res['warning_count']})")
        if res["critical"]:
            print("CRITICAL:")
            for c in res["critical"]:
                print(f"  - {c}")
        if res["warnings"]:
            print("WARNINGS:")
            for w in res["warnings"]:
                print(f"  - {w}")
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
