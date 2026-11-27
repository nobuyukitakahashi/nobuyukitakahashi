#!/usr/bin/env python3
"""
nobuyukitakahashi 組織整合性・品質機械監査スクリプト (07_QA_Dept)
- ルールファイル 24,000 バイト上限 ＆ UTF-8 (BOMなし) 検証
- 全スキル SKILL.md YAML Frontmatter ＆ 相対リンク検証
- INDEX.md 全12ジャンル見出し整合 ＆ 相対リンク実在性検証
- 04_Delivery_Dept/outputs/<genre>/ 直置きファイル違反検出
- プラグイン hooks.json / JS 構文検証
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

GENRES = [
    "blender",
    "illustrator",
    "photoshop",
    "davinci",
    "writing",
    "premiere",
    "aftereffects",
    "moho",
    "pano2vr",
    "krpano",
    "ptgui",
    "web",
]

RULE_LIMIT_BYTES = 24_000
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def has_utf8_bom(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            return f.read(3) == b"\xef\xbb\xbf"
    except OSError:
        return False


FENCE_RE = re.compile(r"```[\s\S]*?```")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def check_relative_links(md_path: Path, root: Path) -> list[str]:
    broken: list[str] = []
    text = md_path.read_text(encoding="utf-8")
    cleaned = INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))
    for m in LINK_RE.finditer(cleaned):
        raw_target = m.group(1).strip()
        if not raw_target or raw_target.startswith(("http://", "https://", "mailto:", "#", "file:///")):
            continue
        target = raw_target.split("#", 1)[0].strip()
        if not target:
            continue
        decoded = unquote(target)
        resolved = (md_path.parent / decoded).resolve()
        if not resolved.exists():
            broken.append(f"{md_path.relative_to(root).as_posix()} -> {raw_target}")
    return broken


def parse_frontmatter(md_path: Path) -> tuple[bool, str]:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return False, "Missing YAML frontmatter start"
    lines = text.splitlines()
    end_idx = None
    for i in range(1, min(len(lines), 40)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return False, "Missing YAML frontmatter closing ---"
    fm_block = "\n".join(lines[1:end_idx])
    if not re.search(r"^name:\s*\S+", fm_block, re.MULTILINE):
        return False, "Missing 'name:' in frontmatter"
    if not re.search(r"^description:\s*", fm_block, re.MULTILINE):
        return False, "Missing 'description:' in frontmatter"
    return True, "OK"


def run_audit(root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict = {}

    # 1. Rules size, BOM, and links
    rule_files: list[Path] = []
    for rel in [
        "AGENTS.md",
        ".agents/rules/global-policy.md",
        ".agents/plugins/global-master-rules/rules/AGENTS.md",
    ]:
        p = root / rel
        if p.exists():
            rule_files.append(p)
        else:
            errors.append(f"Missing core rule file: {rel}")

    for d in sorted(root.iterdir()):
        if d.is_dir() and re.match(r"^\d{2}_", d.name):
            am = d / "AGENTS.md"
            if am.exists():
                rule_files.append(am)
            else:
                errors.append(f"Missing department AGENTS.md: {d.name}/AGENTS.md")

    total_rule_bytes = 0
    for rf in rule_files:
        sz = rf.stat().st_size
        total_rule_bytes += sz
        rel = rf.relative_to(root).as_posix()
        if sz > RULE_LIMIT_BYTES:
            errors.append(f"Rule exceeds 24,000B limit ({sz}B): {rel}")
        if has_utf8_bom(rf):
            errors.append(f"UTF-8 BOM detected: {rel}")
        for brk in check_relative_links(rf, root):
            errors.append(f"Broken rule link: {brk}")
    metrics["rule_files_count"] = len(rule_files)
    metrics["rule_files_total_bytes"] = total_rule_bytes

    # 2. Skills frontmatter, BOM, and links
    skills_dir = root / ".agents" / "skills"
    skill_count = 0
    if skills_dir.exists():
        for sd in sorted(skills_dir.iterdir()):
            if not sd.is_dir():
                continue
            sk = sd / "SKILL.md"
            if not sk.exists():
                errors.append(f"Skill directory missing SKILL.md: {sd.name}")
                continue
            skill_count += 1
            if has_utf8_bom(sk):
                errors.append(f"UTF-8 BOM detected: .agents/skills/{sd.name}/SKILL.md")
            ok, msg = parse_frontmatter(sk)
            if not ok:
                errors.append(f"Invalid frontmatter in {sd.name}/SKILL.md: {msg}")
            for brk in check_relative_links(sk, root):
                errors.append(f"Broken skill link: {brk}")
    metrics["skills_count"] = skill_count

    # 3. Delivery INDEX.md & 12-genre integrity
    idx_path = root / "04_Delivery_Dept" / "outputs" / "INDEX.md"
    if not idx_path.exists():
        errors.append("Missing 04_Delivery_Dept/outputs/INDEX.md")
    else:
        idx_sz = idx_path.stat().st_size
        metrics["index_bytes"] = idx_sz
        if has_utf8_bom(idx_path):
            errors.append("UTF-8 BOM detected in 04_Delivery_Dept/outputs/INDEX.md")
        if idx_sz > 30_000:
            warnings.append(f"INDEX.md is large ({idx_sz}B > 30KB); summarize remarks.")
        idx_text = idx_path.read_text(encoding="utf-8")
        for g in GENRES:
            if f"`outputs/{g}/`" not in idx_text:
                errors.append(f"INDEX.md missing section header for genre: outputs/{g}/")
        for brk in check_relative_links(idx_path, root):
            errors.append(f"Broken INDEX.md link: {brk}")

    # 4. Direct files in 04_Delivery_Dept/outputs/<genre>/
    direct_violations: list[str] = []
    for g in GENRES:
        gp = root / "04_Delivery_Dept" / "outputs" / g
        if not gp.exists():
            errors.append(f"Missing delivery genre directory: 04_Delivery_Dept/outputs/{g}")
            continue
        for item in gp.iterdir():
            if item.is_file() and item.name != ".gitkeep":
                direct_violations.append(item.relative_to(root).as_posix())
    if direct_violations:
        for v in direct_violations:
            errors.append(f"Direct file outside project subfolder: {v}")
    metrics["direct_delivery_violations"] = len(direct_violations)

    # 5. Hooks & plugin JSON/JS validation
    hooks_json = root / ".agents" / "plugins" / "global-master-rules" / "hooks.json"
    guard_js = root / ".agents" / "plugins" / "global-master-rules" / "scripts" / "org_guard.js"
    if hooks_json.exists():
        try:
            json.loads(hooks_json.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Invalid hooks.json: {exc}")
        if has_utf8_bom(hooks_json):
            errors.append("UTF-8 BOM detected in hooks.json")
    else:
        warnings.append("Plugin hooks.json not found.")

    if guard_js.exists():
        if has_utf8_bom(guard_js):
            errors.append("UTF-8 BOM detected in org_guard.js")
        proc = subprocess.run(["node", "--check", str(guard_js)], capture_output=True, text=True)
        if proc.returncode != 0:
            errors.append(f"org_guard.js syntax error: {proc.stderr.strip()}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "metrics": metrics,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify nobuyukitakahashi organization integrity")
    parser.add_argument("--root", default="", help="Repository root path")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.root:
        root = Path(args.root).resolve()
    else:
        root = Path(__file__).resolve().parents[2]

    result = run_audit(root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"STATUS: {result['status']}")
        print(f"METRICS: {json.dumps(result['metrics'], ensure_ascii=False)}")
        if result["warnings"]:
            print("WARNINGS:")
            for w in result["warnings"]:
                print(f"  - {w}")
        if result["errors"]:
            print("ERRORS:")
            for e in result["errors"]:
                print(f"  - {e}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
