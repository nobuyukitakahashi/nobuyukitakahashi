Add-Type -AssemblyName System.Drawing

$draftDir = "g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
$framesDir = Join-Path $draftDir "frames_raw"

. "$draftDir\build_contact_sheets.ps1"

$offsets15_65 = 15..65 | ForEach-Object { $_ * 30 }
Build-Sheet -Offsets $offsets15_65 -OutName "contact_15s_to_65s.png" -Cols 5
