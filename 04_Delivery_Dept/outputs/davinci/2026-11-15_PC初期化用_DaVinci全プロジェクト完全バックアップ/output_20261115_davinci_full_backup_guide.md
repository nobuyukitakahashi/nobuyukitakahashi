# 🎬 PC初期化前・DaVinci Resolve Studio 全プロジェクト完全バックアップ＆復元手順書

- **バックアップ実行日時**: 2026-11-15 11:01 (JST)
- **対象ソフト**: DaVinci Resolve Studio 21.2
- **対象プロジェクト数**: 全15プロジェクト（エクスポート成功率 **15/15 = 100%**）
- **二重保存先**:
  1. **Googleドライブ（クラウド自動同期・納品フォルダ）**:
     [`04_Delivery_Dept/outputs/davinci/2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ/`](file:///g:/マイドライブ/git/nobuyukitakahashi/04_Delivery_Dept/outputs/davinci/2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ/)
  2. **内蔵Dドライブ（ローカル高速SSDミラー）**:
     [`D:\DvinchiProject\2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ\`](file:///D:/DvinchiProject/2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ/)

---

## 📦 1. バックアップフォルダ内の収録データ構成

| サブフォルダ / ファイル名 | 内容と用途 | 容量目安 |
| :--- | :--- | :---: |
| **[`RESTORE_DAVINCI_PROJECTS.ps1`](file:///g:/マイドライブ/git/nobuyukitakahashi/04_Delivery_Dept/outputs/davinci/2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ/RESTORE_DAVINCI_PROJECTS.ps1)** | **PC初期化後の「1クリック自動復元スクリプト（PowerShell）」** | 3 KB |
| **`01_DRP_個別プロジェクトファイル一式/`** | 全15プロジェクトの個別アーカイブファイル（`.drp`、スチル＆LUT同梱） | 約 37.7 MB |
| **`02_Resolve_Project_Library_丸ごとバックアップ/`** | `Resolve Project Library` フォルダ一式 ＋ 圧縮ZIP（`Resolve_Project_Library_FullBackup_20261115.zip`） | 非圧縮 60.3 MB<br>（ZIP 8.72 MB） |
| **`03_Custom_Settings_LUT_Templates/`** | カスタム設定（`Fusion` テンプレート、`.LUT`、`Fairlight` プリセット、`D:\DvinchiProject\.gallery` スチル一式） | 約 19.5 MB |
| **`04_Cドライブ参照素材退避/`** | Cドライブ（OneDrive配下）で現存していたプロジェクト参照メディア2点（`cvn_official_1084_240_rgb.png`、`活育財団_NextEducationAward2026TP部門_ver.2.mp4`） | 約 42.1 MB |

---

## 📋 2. バックアップ済み全15プロジェクト一覧（`.drp` 出力検証済）

| # | プロジェクト名 | `.drp` ファイル名 | サイズ | 主な元素材（動画/音声）の場所 |
| :---: | :--- | :--- | :---: | :--- |
| 1 | 2026-04-15 桐林定例区会前_EPSON予備説明 | `2026-04-15 桐林定例区会前_EPSON予備説明.drp` | 69.2 KB | 外付けドライブ (`H:`) |
| 2 | 2026-04-24 竜丘地域自治会総会EPSON説明 | `2026-04-24 竜丘地域自治会総会EPSON説明.drp` | 83.7 KB | 旧Desktop (`DJI_001`) |
| 3 | 2026-04-25 長田家お宮参り | `2026-04-25 長田家お宮参り.drp` | 73.9 KB | 外付けドライブ (`H:`) |
| 4 | 2026-04-26　桐林区民総会EPSONバイオマス発電所計画中止説明会 | `2026-04-26　桐林区民総会EPSONバイオマス発電所計画中止説明会.drp` | 179.8 KB | 外付けドライブ (`H:`) |
| 5 | 2026-11-13 南信州広域連合へ要望書提出 | `2026-11-13 南信州広域連合へ要望書提出.drp` | 2,927.1 KB | 外付け (`H:`) / Googleドライブ (`G:`) |
| 6 | 2026-11-13 南信州広域連合議会 全員協議会 | `2026-11-13 南信州広域連合議会 全員協議会.drp` | 472.5 KB | 外付け (`H:`) / Googleドライブ (`G:`) |
| 7 | 2026videoletter | `2026videoletter.drp` | 419.8 KB | Googleドライブ (`G:`) |
| 8 | 2026牧野ゼミ紹介V | `2026牧野ゼミ紹介V.drp` | 512.0 KB | `D:` / 旧Desktop |
| 9 | 2026牧野ゼミ紹介Vのコピー | `2026牧野ゼミ紹介Vのコピー.drp` | 474.0 KB | `D:` / 旧Desktop |
| 10 | 2027牧野ゼミ紹介 | `2027牧野ゼミ紹介.drp` | 659.0 KB | `D:` / 外付け (`H:`) / 旧Desktop |
| 11 | APVTEST | `APVTEST.drp` | 62.4 KB | 外付けドライブ (`H:`) |
| 12 | WEB企業説明会2027PV | `WEB企業説明会2027PV.drp` | 23,842.9 KB | 外付けドライブ (`H:`) |
| 13 | 令和8年度飯田高校同窓会定期総会 | `令和8年度飯田高校同窓会定期総会.drp` | 7,057.2 KB | 外付けドライブ (`H:`) |
| 14 | 原勉cvn CM | `原勉cvn CM.drp` | 843.0 KB | `04_Cドライブ参照素材退避/原勉cvn_CM/` 退避済 |
| 15 | 活育財団_NextEducationAward2026TP | `活育財団_NextEducationAward2026TP.drp` | 49.5 KB | 外付け (`H:`) ＋ `04_Cドライブ参照素材退避/` 退避済 |

---

## ⚠️ 3. PC初期化する「直前」に確認する2つのポイント

1. **DaVinci Resolve Studio ライセンス認証の解除（推奨）**
   - DaVinci Resolve を開き、上部メニュー **「ヘルプ (Help)」➔「ライセンス認証を解除 (Deactivate License)」** をクリックしてからPCを初期化すると、ライセンス認証枠を消費せず再インストール後にスムーズに認証できます。
2. **Cドライブ以外のドライブ（`D:` / `E:` / 外付け `H:`）の取り扱い**
   - Windows初期化時に **「システムドライブ（Cドライブ）のみ初期化する」** を選べば、`D:\DvinchiProject` や `E:\` の動画素材はそのまま残ります（念のため外付けHDDはUSBケーブルを抜いてからPC初期化を行うと、誤消去リスクがゼロになります）。

---

## 🚀 4. PC初期化後の復元手順（3つの方法から選べます）

### 方法A：【最速・推奨】1クリック自動復元スクリプトを実行する
1. PC初期化後、**DaVinci Resolve Studio** をインストールします（※まだ起動しないか、一度起動したら終了しておきます）。
2. 本フォルダ内の **[`RESTORE_DAVINCI_PROJECTS.ps1`](file:///g:/マイドライブ/git/nobuyukitakahashi/04_Delivery_Dept/outputs/davinci/2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ/RESTORE_DAVINCI_PROJECTS.ps1)** を右クリックし、**「PowerShellで実行」** をクリックします。
3. 自動的に `C:\Users\<ユーザー名>\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Resolve Project Library` とカスタム設定が復元されます。
4. DaVinci Resolve を起動すると、**全15プロジェクトが初期化前と全く同じ状態で一覧に表示されます**。

### 方法B：DaVinci Resolve の画面（GUI）からデータベースを接続する
1. DaVinci Resolve を起動し、**プロジェクトマネージャー（Project Manager）** 画面を開きます。
2. 左上のアイコンからサイドバー（プロジェクトライブラリ一覧）を表示し、下部の **「プロジェクトライブラリを追加 (Add Project Library)」** をクリックします。
3. 上部の **「接続 (Connect)」** タブを選び、名前に `Local Database (Restored)` 等を入力し、**「場所 (Location)」** で本バックアップ内の
   `02_Resolve_Project_Library_丸ごとバックアップ\Resolve Project Library\Resolve Projects`
   を指定して「追加」を押すと、全15プロジェクトが一括で読み込まれます。

### 方法C：必要なプロジェクトだけを `.drp` から個別に読み込む
1. DaVinci Resolve のプロジェクトマネージャー画面で右クリック ➔ **「プロジェクトの読み込み (Import Project...)」** を選択します。
2. `01_DRP_個別プロジェクトファイル一式\` 内の任意の `.drp` ファイルを選択すると、そのプロジェクトが即座に復元されます。

---

## 🔗 5. 初期化後に「Media Offline（赤い画面）」が出た場合の1クリック再リンク手順
PC初期化後、外付けHDD等のドライブ文字（`H:` 等）が変わった場合は、クリップが「Media Offline」と表示されることがあります。以下の手順で一瞬で繋がります：
1. メディアプール（Media Pool）でオフラインのクリップを選択し、左上の赤いチェーンアイコン（または右クリック ➔ **「選択したクリップを再リンク (Relink Selected Clips...)」**）をクリックします。
2. 元動画が入っている外付けHDDやフォルダを選択して「OK」を押すと、フォルダ内を自動検索してすべての動画・音声が一括で元通りにリンクされます。
