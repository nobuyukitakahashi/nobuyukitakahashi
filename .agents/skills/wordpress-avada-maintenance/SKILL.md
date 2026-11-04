---
name: wordpress-avada-maintenance
description: |
  Comprehensive guide and operational runbook for WordPress and Avada Theme (Fusion Builder) development, maintenance, and safe deployment.
  Use when managing WordPress sites running Avada, editing Fusion Builder layouts/shortcodes, managing child themes, interacting via WP-CLI or SSH, scheduling timed post/page content swaps, handling Windows PowerShell UTF-8 character encoding, or managing page templates, post meta, and Avada caches.
---

# WordPress & Avada Maintenance Guide

This skill provides operational standards, architectural patterns, and safety guardrails for maintaining, developing, and deploying WordPress websites powered by the **Avada Theme (7.x+)** and **Fusion Builder**.

---

## 1. Avada & Fusion Builder Shortcode Standards

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

