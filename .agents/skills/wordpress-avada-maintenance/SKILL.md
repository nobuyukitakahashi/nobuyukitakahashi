---
name: wordpress-avada-maintenance
description: >-
  WordPress・Avada Theme（Fusion Builder）・子テーマ・WP-CLI/SSH・日時切替・UTF-8保守の運用ランブック。
  Avadaサイト改修やWordPress保守作業時に使用。
---

# WordPress & Avada Maintenance Guide

This skill provides operational standards, architectural patterns, and safety guardrails for maintaining, developing, and deploying WordPress websites powered by the **Avada Theme (7.x+)** and **Fusion Builder**.

---

## 1. Avada & Fusion Builder Shortcode Standards

### 1.0 Core Principle: Back-End Builder Maintainability & Refined Design (MANDATORY)
For all WordPress sites built with the **Avada** theme set (`https://avada.com/`):
- **Research Latest Shortcodes & Official Samples**: Always research and utilize the latest standard shortcodes, elements, and layout patterns supported by the installed **Avada Back-End Builder (Fusion Builder)** and official Avada documentation/samples (`https://avada.com/`).
- **Human-Maintainable Structure**: Avoid raw HTML/inline CSS/custom JS workarounds whenever a native Fusion Builder element exists. Structure every section using standard containers, rows, columns, and native Fusion elements so that human editors can easily inspect, edit, and maintain both appearance and functionality directly in the WordPress **Back-End Builder** UI.
- **Refined Design & Functionality**: Ensure spacing, typography, color harmony, responsive visibility, and interactive behavior are polished and cohesive.

### 1.1 Structural Hierarchy
Fusion Builder pages must strictly adhere to the nesting structure:
```text
[fusion_builder_container]
  └── [fusion_builder_row]
        └── [fusion_builder_column]
              └── [elements: fusion_title, fusion_text, fusion_image, etc.]
```

### 1.2 Essential Page Meta (Crucial for Avada Rendering)
When creating or cloning pages via WP-CLI or database, ensure these three meta keys are present:
1. `_wp_page_template`: Set to `100-width.php` (required for modern Avada full-width layouts).
2. `fusion_builder_status`: Set to `active` (without this, WordPress treats the page as plain text).
3. `_fusion`: Serialized array containing Avada page options (padding, headers, sliders, page title bar).
4. `_fusion_google_fonts`: Array defining any custom Google Fonts loaded for the page.

### 1.3 Responsive Controls
Avada relies heavily on visibility flags:
- `hide_on_mobile="small-visibility"` (hidden on mobile, shown on tablet/desktop)
- `hide_on_mobile="medium-visibility,large-visibility"` (shown only on mobile)
- Always verify both desktop buttons and mobile image/carousel alternatives when modifying navigation or action buttons.

---

## 2. Safe Staging & Zero-Downtime Deployment Workflow

### 2.1 The Preview-First Principle
Never edit a critical live page directly. Follow this 4-step pipeline:
1. **Clone to Preview**:
   Create a preview page (e.g. slug: `11ch-preview`, title with `(作業用プレビュー)`).
   Add noindex to prevent search engine indexing:
   `wp post meta update <preview_id> _yoast_wpseo_meta-robots-noindex 1`
2. **Apply Updates**:
   Construct and update shortcodes on the preview post.
3. **Verify with User**:
   Provide the live preview URL for desktop and mobile verification.
4. **Deploy**:
   Swap content into production, either immediately or via scheduled release.

### 2.2 Scheduled Auto-Swap (2-Layer Bulletproof Mechanism)
When content needs to release at a specific future timestamp (e.g. `2026-10-01 00:00:00 JST`):
1. **Layer 1: WP-Cron Event**:
   Register a non-repeating cron event with GMT/UTC timestamp:
   ```bash
   wp cron event schedule <action_hook> <timestamp_utc>
   ```
2. **Layer 2: `template_redirect` Instant Fallback**:
   To eliminate reliance on visitor traffic triggering cron right at midnight, register a fallback in `functions.php`:
   ```php
   add_action( 'template_redirect', function() {
       if ( is_page( <live_id> ) && ! get_option( '<option_key>' ) ) {
           if ( time() >= <target_timestamp> ) {
               // Execute swap function immediately before rendering
               do_action( '<action_hook>' );
           }
       }
   } );
   ```
   This guarantees 0-second latency for the very first visitor who accesses the page after release time.

---

## 3. Windows & PowerShell Encoding Guardrails (CRITICAL)

> [!WARNING]
> **NEVER PIPE UTF-8 POST CONTENT VIA POWERSHELL STDIN TO WP-CLI.**

### The Problem
On Windows, piping commands like `Get-Content file.html | wp post update ...` converts UTF-8 strings into the Windows console's active codepage (CP932 / Shift-JIS). When received by Linux/WordPress, Japanese and other multi-byte characters become irreversibly corrupted (mojibake).

### The Safe Procedure
1. Save the file locally as clean UTF-8 without BOM.
2. Transfer the file directly to the remote server using `scp`:
   ```powershell
   scp -P <port> local_file.html <user>@<host>:~/remote_file.html
   ```
3. Execute WP-CLI on the server reading directly from that server-side file:
   ```bash
   wp post update <id> ~/remote_file.html
   ```
4. Verify the database content contains pure UTF-8 multibyte characters.

---

## 4. WP-CLI Remote Operations & Server Commands

### 4.1 Heteml / Non-Standard SSH Environments
On shared hosting (such as Heteml), non-interactive SSH sessions often have restricted `$PATH`.
- Always specify the explicit PHP binary or add `/usr/local/bin:/usr/bin:/bin` to `PATH`.
- Quote aliases in PowerShell to prevent parameter splatting: `wp '@alias'` instead of `wp @alias`.
- Execute WP-CLI using full path if needed: `~/bin/wp --path=/path/to/wordpress`.

### 4.2 Cache Invalidation
Whenever post content, shortcodes, or child theme assets are updated:
1. `wp cache flush` (Flushes WordPress object cache).
2. Clear Avada Fusion Cache if dynamic CSS/JS changes:
   ```bash
   wp eval 'if ( class_exists( "Fusion_Cache" ) ) { Fusion_Cache::reset_all_caches(); }'
   ```

---

## 5. Child Theme & Custom Shortcode Guidelines

- Child theme folder: `themes/Avada-Child-Theme/`
- Always enqueue child styles with parent theme dependency.
- For date-dependent content, use `current_time( 'timestamp' )` or `wp_date()` to respect WordPress's configured timezone (`Asia/Tokyo`).
- Keep all custom post-types, shortcodes, and cron actions documented in `functions.php` with clear docblocks.

---

## 6. Autonomous Cross-Device Git & GitHub Synchronization

When working across multiple machines or handoffs:
1. **Pre-Task Check & Pull**:
   - Always run `git pull origin master` before making modifications to ensure updates from other machines are loaded.
2. **Post-Task Commit & Push**:
   - Without waiting for explicit user prompts, always stage, commit, and `git push origin master` all project files, scripts, and theme changes at the end of each task.

---

## 7. Web・フロントエンド・CMS 4大検証義務（表層チェック・手抜き禁止）

UI・レイアウト・CSS・HTML・Avadaショートコード改修時は、以下の4対策をすべて満たしてから完了報告する：
1. **要素単位の深層ジオメトリ検証**: `document.documentElement.scrollWidth` だけで合格判定せず、内部カラムラッパー（`.fusion-column-wrapper` 等）の行単位の左右余白対称性（`getBoundingClientRect()` による `left` と `viewportWidth - right` の一致）、および `overflow-x: auto` コンテナ・テーブル要素（`el.scrollWidth <= el.clientWidth`）・セル見切れ・極小幅1文字折り返しまで要素単位で検査する。
2. **親テーマ・フレームワーク実装ソースの事前確認**: CSS上書きやショートコード実装前に、親テーマ（PHP/CSS/JS）の実ソースコード・登録定義を直接検索読解し、インライン `!important` や `@media` 強制指定（`white-space: nowrap`、`width: calc(...) !important` 等）を特定してから実装する。
3. **実ブラウザ DOM / CSSOM・`getComputedStyle` 実機検証**: 静的文字列一致で推測せず、ヘッドレスブラウザ上の実DOMおよび `window.getComputedStyle(el)`（インライン `style` 再シリアライズや詳細度競合含む）でスタイル適用結果を検証する。
4. **3デバイス実画面スクリーンショットの `read_file` 目視監査**: テストの `Exit Code 0` だけで完了報告せず、PC（`1920px`）・タブレット（`768px`）・スマホ（`375px`）の3画面を撮影し、`read_file` で視覚的に「余白対称性」「テーブル枠内横スクロール・文字潰れ」「要素重なり・崩れ」を確認する。

---

## 8. 共通運用ガバナンス（全 WordPress 保守サイト単一ソース）

各サイトの `AGENTS.md` へ重複コピーせず、以下を全 WordPress 保守サイトの共通基準とする：
1. **作業開始・再開時の応答原則**: ユーザーから「再開OK？」「始めます」等の挨拶・再開確認のみを受けた段階では、裏で Git/SSH/疎通コマンドを無闇に実行せず即座に応答し、具体的な更新指示を受けてから `start-maint.ps1` / `fetch_pages.py` 等を必要最小限で実行する。
2. **デュアル保守（管理画面手動編集 × WP-CLI）4原則**:
   - 更新前に必ず `fetch_pages.py`（または `start-maint.ps1`）で最新ライブ状態を取得し、スタッフ手動編集の上書きを防ぐ。
   - 生の `<iframe>` / `<script>` はページ本文へ直書きせず子テーマ `functions.php` でショートコード化する。
   - `wp_revisions_to_keep = 30` と `fusion_builder_status = active` / `_wp_page_template = 100-width.php` を維持する。
   - 反映後は `wp cache flush` ＆ Avada/WP-Optimize キャッシュクリアを実施する。
3. **5部門分離・サブエージェント分業体制（`global-master-rules` §1・§5 統合版）**:
   - 単純質問・1ファイル軽微誤字修正を除き、①**統括（メイン）** ➔ ②**実装計画（`planner`, 読取専用）** ➔ ③**データバックアップ（`backup-manager`）** ➔ ④**更新実装（`implementer`）** ➔ ⑤**独立目視検証（`visual-qa-verifier`, 読取専用・§7 準拠）** に分離実行する。
   - 着手前に「部門・担当・推奨LLM（軽微: `flash`/`gemini-4-hydrogen-medium`、横断・視覚監査: `pro`/`gemini-4-neon-high`・`argon-high`）・実行方式（`invoke_subagent`/`swarm`）」の表を1回提示して承認を得る（`global-master-rules` §1 の単体ゲートと二重提示しない）。
   - `visual-qa-verifier` が `global-master-rules` §5 の `qa-verifier` を兼ね、`PASS` まで完了報告しない。
4. **バックアップ圧縮・世代ローテーション**: ローカル `backups/` の DB ダンプは `.sql.gz` 圧縮で直近5〜10世代のみ保持し、`.gitignore` で Git 追跡から除外する。



