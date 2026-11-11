# 法務・コンプライアンス審査レポート：kinoshita_aimeikai_2027（木下建設株式会社「愛名会 2027企業案内」リクルートサイト更新一式）
- **審査日**: 2026年11月11日
- **該当トリガー領域**:
  1. **広告・表示規制領域**（職業安定法第5条の4・第65条「求人等に関する情報の的確な表示義務」、青少年の雇用の促進等に関する法律（若者雇用促進法）第7条「青少年雇用情報の提供」、労働基準法第15条「労働条件の明示」、景品表示法上の優良誤認防止）
  2. **知的財産・引用・AI権利領域**（人物イラスト使用時における「※イラストはイメージです」表示の徹底、公的認証ロゴの適正表示）
  3. **個人情報・機密情報（PII / NDA）領域**（個人情報保護法に基づく先輩社員のイニシャル匿名化措置、公開窓口としての採用担当者実名表記の適法性確認）
  4. **プラットフォーム規約・物理仕様領域**（学校法人名古屋電機学園「愛名会 2027企業案内」更新作業マニュアルの技術的・物理的制約遵守）
- **総合判定ステータス**: `[APPROVED: 承認（法的リスク対策済・本番運用時の推奨注記および人間最終確認事項あり）]`

---

### 1. リーガル審査サマリー

上流部門（`01_Research_Dept`、`02_Creative_Dept/{writing,photoshop}`、`03_Marketing_Dept`）が作成した木下建設株式会社「愛名会 2027企業案内（会員番号：101592）」掲載用の中間成果物一式について、採用・求人関連法令（2026年現行基準）および愛名会更新マニュアルの物理仕様の観点から厳格なリーガル・コンプライアンス審査を実施した。

**【審査結論】**
1. **求人・採用表示の適正性（職業安定法・若者雇用促進法・労働基準法）**:
   - 初任給（`289,000円`）について「月額・手当込み／名古屋支店勤務・令和9年4月入社基準」と条件・基準時点が明記され、賞与（`年3回`）についても「令和7年度実績」と過去実績である旨が正確に付記されている。
   - 年間休日（`123日（令和7年度実績）／122日（令和8年度予定）・有給休暇 入社時10日付与`）、従業員数（`131名（2026年6月時点）※2026年10月時点128名`）、売上高（`約82.6億円（82億5,998万円／2026年5月期実績）`）など、愛名会サイト登録値とスライド記載値の時点差がすべて注記付きで統合されており、職業安定法第5条の4（誤解を生じさせる表示の禁止）に完全適合している。
   - 勤務地についても「名古屋支店管内（昭和区阿由知通）勤務が基本」「本社（飯田市）での大規模インフラ土木・建築希望も歓迎」と明記され、転居を伴う全国転勤の有無や配属範囲に関する求職者の誤認リスクが解消されている。
   - なお、正式な求人票（ハローワーク・大学キャリアセンター提出票）との整合性確保のため、**固定残業代（みなし残業代）の有無・時間数・金額・超過分別途支給の旨**については、本番運用時の補足注記または正式求人票への誘導文言として併記することを推奨する（下記セクション2・3参照）。
2. **原典スライドからの校正12箇所の適法性・事実整合性**:
   - 動画専用表記（`CM1〜3 15sec`、`この動画の流れ`、秒数タイムコード）の撤廃、第3章への「名古屋支店の施工実績29件（旧P.23）」移動、表記揺れ（「先輩のもとで」）統一、代表取締役社長氏名「木下 勝貴」の補記、募集対象スコープの拡大（建築学科＋社会基盤学科＋愛工大名電高）のすべてが原典ファクトに基づき適法かつ正確に処理されている。
   - 特に旧P.20における「`R.Kさん`」のイニシャル重複解消にあたり、根拠のない架空イニシャル（`T.Sさん` 等）を捏造せず、全28Pピッチブック（P.18）では「`名古屋支店建築工事部 2025年入社の先輩（建築施工担当）`」と事実表記し、愛名会サイトの声枠（枠2）では代表1枠の「`R.K さん（先輩社員）`」へ統合した判断は、ハルシネーション防止および職業安定法上の虚偽表示防止の観点から極めて適切である。
3. **肖像権・個人情報保護（PII）およびイラスト注記**:
   - 若手・女性社員4名についてはイニシャル表記（`H.Kさん`、`R.Kさん`、`S.Kさん`、`A.Kさん`）およびイラスト使用により個人特定リスク（PII）が適切に保護されており、かつ全スライド・全ポートレート画像（`voice01`〜`voice04`）・全コメント末尾に **`※イラストはイメージです（ご本人ではありません）` / `（※掲載イラストはイメージです）`** が明記されている。
   - 採用担当者「向野 浩幸（こうの ひろゆき）」氏の氏名・所属（総務本部総務部）・連絡先（本社TEL `0265-22-2780`、名古屋支店TEL `052-741-6220`、E-mail `hr@kinoken.co.jp`）は、愛名会「2027企業案内」公開ページ（`https://aimeikai.net/detail/101592`）ですでに公開されている公式採用窓口情報であり、個人情報保護法上の第三者提供制限やプライバシー侵害の問題は生じない。
4. **愛名会アップロード仕様（物理的・技術的制約）の完全適合**:
   - 実ファイル検証の結果、PDF2点・JPG11点のファイル形式、ファイルサイズ（全点5MB以下）、ファイル名規則（半角英数字小文字のみ）、および `target[message][]` の改行なし1行テキスト仕様のすべてが100%適合していることを確認した（下記セクション4に実測値を記載）。

---

### 2. リスク箇所の指摘と安全な代替表現（修正指示・運用推奨テーブル）

現時点の中間成果物に法令違反となる致命的欠陥は存在しないが、広報解禁（3月1日）および説明会運用時に求職者（学生・保護者・大学キャリアセンター）との間で解釈の齟齬を生じさせないため、以下の3点について「より安全な代替・補足表現」を提示する。

| 対象ファイル・箇所 | 原文（現行表現） | 抵触リスクのある法令・規約・理由 | 安全な代替表現（そのまま使える修正・補足文案） |
| :--- | :--- | :--- | :--- |
| [`content_kinoshita_aimeikai_2027.md`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/writing/final_outputs/content_kinoshita_aimeikai_2027.md) P.24 / [`promo_kinoshita_aimeikai_2027.md`](file:///g:/マイドライブ/git/nobuyukitakahashi/03_Marketing_Dept/promos/promo_kinoshita_aimeikai_2027.md) 長文告知 | `初任給 289,000円（月額・手当込み／名古屋支店勤務・R9.4入社基準）` | **職業安定法第5条の4・労働基準法第15条（固定残業代・諸手当の内訳明示）**:<br>広報用ピッチブック・SNS告知としては現行表記で適法だが、学生が「基本給のみで28.9万円か、固定残業代が含まれるか」を誤認しないよう、正式求人票との接続注記を添えるとより安全である。 | `初任給 289,000円（月額・諸手当込み／名古屋支店勤務・令和9年4月入社基準 ※基本給・諸手当の内訳および固定残業代の有無等の詳細は、愛名会登録の正式求人票または募集要項をご確認ください）` |
| [`content_kinoshita_aimeikai_2027.md`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/writing/final_outputs/content_kinoshita_aimeikai_2027.md) 枠2 / [`promo_kinoshita_aimeikai_2027.md`](file:///g:/マイドライブ/git/nobuyukitakahashi/03_Marketing_Dept/promos/promo_kinoshita_aimeikai_2027.md) 枠2 (`target[title][]`) | `ここより良い職場はない！地図と街に残り続ける仕事を一緒にしましょう` | **職業安定法第65条・景品表示法（最上級・主観的評価表現の文脈明確化）**:<br>先輩社員個人の感想（カギ括弧付き引用）として「ここより良い職場はない！」と述べること自体は違法ではないが、タイトル欄で単独表示される際、客観的No.1表示ではなく「先輩社員個人の実感」であることを明確にするとより堅牢である。 | **【現行のままでも利用可／より堅牢な代替タイトル案】**:<br>`「ここより良い職場はない！」と実感。地図と街に残る仕事を一緒にしましょう` |
| [`content_kinoshita_aimeikai_2027.md`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/writing/final_outputs/content_kinoshita_aimeikai_2027.md) P.22 / [`kinoshita_photo03.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/kinoshita_photo03.jpg) | `奨学金の返還を会社が支援：月2.5万円以内 × 入社10年目まで（最大300万円相当）` | **労働条件・福利厚生制度の適用条件誤認防止**:<br>「月2.5万円以内」と上限表記されているため優良誤認には当たらないが、対象となる奨学金の種類や社内規程に基づく支給要件がある旨を注記しておくと入社後のトラブルを防げる。 | `奨学金返還支援制度：月2.5万円以内×入社10年目まで（10年間で最大300万円相当 ※当社規程および実際の返還額に応じ支給）` |

---

### 3. 必須表記・免責事項（ディスクレーマー）の追加提案

- **新着情報PDF掲載時・キャリアセンター案内文への推奨付記文言**:
  ```text
  ※本資料に記載の初任給（289,000円／月額・手当込み）は名古屋支店勤務・令和9年4月入社予定者の基準額です。賞与（年3回・令和7年度実績）、年間休日（令和7年度実績123日／令和8年度予定122日）、平均残業時間（若手月平均11時間）等は実績値・予定値であり、配属部署や年度により変動する場合があります。基本給・諸手当の内訳等の詳細な労働条件は、最新の求人票および募集要項にてご確認ください。
  ※先輩社員紹介に使用している人物イラストはすべてイメージです（ご本人ではありません）。
  ```
- **【人間オーナー・採用ご担当者（向野様）への最終確認事項（エスカレーション）】**:
  1. **旧P.20（新P.18）「R.Kさん」2名重複の事実確認**: 原典スライドP.20の中央と右の2名がどちらも `R.Kさん` となっていた点について、本制作物では架空イニシャルを作らず「右：名古屋支店建築工事部 2025年入社の先輩（建築施工担当）」として安全に処理済みです。もし実際のイニシャルが判明し、別イニシャルへの差し替えをご希望の場合は最終入稿前に反映可能です。
  2. **先輩社員ポートレート画像の実写差し替え可否**: 現在 `voice01_hk.jpg`〜`voice04_ak.jpg` は原典スライドのイラストに `※イラストはイメージです` バッジを合成した適法仕様で作成しています。実写の顔写真へ差し替える場合は、対象社員本人から「採用広報Webサイト（愛名会2027企業案内）への顔写真・所属・コメント掲載に関する同意（肖像権使用許諾）」を取得した上で差し替えてください。

---

### 4. 愛名会「2027企業案内」物理的・技術的仕様コンプライアンス監査結果（実測値）

愛名会マニュアル（[`00_COO/projects/kinoshita_kensetsu/sources/aimeikai_2027_manual.pdf`](file:///g:/マイドライブ/git/nobuyukitakahashi/00_COO/projects/kinoshita_kensetsu/sources/aimeikai_2027_manual.pdf)）のシステム制約に対する全13ファイル＋テキストフィールドの実測検証結果は以下の通りであり、**全項目100%クリア**を確認した。

| 検証対象ファイル / 項目 | ファイルパス | 形式規則 | 実測サイズ | 上限基準 (5MB) | ファイル名規則（半角英数字小文字） | 判定 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **新着情報PDF①（28Pピッチブック）** | [`kinoshita_2027_recruit_pitchbook.pdf`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/writing/final_outputs/kinoshita_2027_recruit_pitchbook.pdf) | PDF (`.pdf`) | **4.00 MB** (4,192,764 B) | 5.00 MB以下 | 適合（任意・英数小文字） | **PASS** |
| **新着情報PDF②（1P説明会チラシ）** | [`kinoshita_2027_briefing_flyer.pdf`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/writing/final_outputs/kinoshita_2027_briefing_flyer.pdf) | PDF (`.pdf`) | **1.73 MB** (1,818,720 B) | 5.00 MB以下 | 適合（任意・英数小文字） | **PASS** |
| **イメージ写真①** | [`kinoshita_photo01.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/kinoshita_photo01.jpg) | JPEG (`.jpg`) | **339.3 KB** (347,442 B) | 5.00 MB以下 | `kinoshita_photo01.jpg`（適合） | **PASS** |
| **イメージ写真②** | [`kinoshita_photo02.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/kinoshita_photo02.jpg) | JPEG (`.jpg`) | **286.1 KB** (292,967 B) | 5.00 MB以下 | `kinoshita_photo02.jpg`（適合） | **PASS** |
| **イメージ写真③** | [`kinoshita_photo03.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/kinoshita_photo03.jpg) | JPEG (`.jpg`) | **364.0 KB** (372,697 B) | 5.00 MB以下 | `kinoshita_photo03.jpg`（適合） | **PASS** |
| **イメージ写真④** | [`kinoshita_photo04.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/kinoshita_photo04.jpg) | JPEG (`.jpg`) | **428.3 KB** (438,583 B) | 5.00 MB以下 | `kinoshita_photo04.jpg`（適合） | **PASS** |
| **イメージ写真⑤** | [`kinoshita_photo05.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/kinoshita_photo05.jpg) | JPEG (`.jpg`) | **360.1 KB** (368,784 B) | 5.00 MB以下 | `kinoshita_photo05.jpg`（適合） | **PASS** |
| **イメージ写真⑥** | [`kinoshita_photo06.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/kinoshita_photo06.jpg) | JPEG (`.jpg`) | **274.7 KB** (281,281 B) | 5.00 MB以下 | `kinoshita_photo06.jpg`（適合） | **PASS** |
| **先輩社員の声① 顔写真** | [`voice01_hk.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/voice01_hk.jpg) | JPEG (`.jpg`) | **68.8 KB** (70,431 B) | 5.00 MB以下 | `voice01_hk.jpg`（適合） | **PASS** |
| **先輩社員の声② 顔写真** | [`voice02_rk.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/voice02_rk.jpg) | JPEG (`.jpg`) | **68.1 KB** (69,770 B) | 5.00 MB以下 | `voice02_rk.jpg`（適合） | **PASS** |
| **先輩社員の声③ 顔写真** | [`voice03_sk.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/voice03_sk.jpg) | JPEG (`.jpg`) | **80.0 KB** (81,882 B) | 5.00 MB以下 | `voice03_sk.jpg`（適合） | **PASS** |
| **先輩社員の声④ 顔写真** | [`voice04_ak.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/voice04_ak.jpg) | JPEG (`.jpg`) | **74.8 KB** (76,620 B) | 5.00 MB以下 | `voice04_ak.jpg`（適合） | **PASS** |
| **採用担当者の声⑤ 顔写真** | [`voice05_kono.jpg`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/photoshop/final_outputs/voice05_kono.jpg) | JPEG (`.jpg`) | **148.7 KB** (152,221 B) | 5.00 MB以下 | `voice05_kono.jpg`（適合） | **PASS** |
| **声枠 `target[message][]` 全5枠** | [`promo_kinoshita_aimeikai_2027.md`](file:///g:/マイドライブ/git/nobuyukitakahashi/03_Marketing_Dept/promos/promo_kinoshita_aimeikai_2027.md) | 1行テキスト | 全5枠 改行なし1行完結 | 改行不可仕様対応 | — | **PASS** |

---
> ※免責注記：本レビューはAIによる法務・コンプライアンスリスクの一次スクリーニングおよび情報整理であり、弁護士法第72条に基づく法的鑑定や法律事務を提供するものではありません。重大な契約締結や法的紛争の可能性がある事案については、必ず人間オーナーおよび顧問弁護士・社会保険労務士等の専門家による最終確認を行ってください。
