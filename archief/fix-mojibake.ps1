function S([int[]]$codes) { return -join ($codes | ForEach-Object { [string][char]$_ }) }
$map = New-Object 'System.Collections.Generic.Dictionary[string,string]'
$map[(S 0x00E2,0x20AC,0x0153)] = [string][char]0x201C # â€œ -> “
$map[(S 0x00E2,0x20AC,0x009C)] = [string][char]0x201C
$map[(S 0x00E2,0x20AC,0x009D)] = [string][char]0x201D # â€\x9d -> ”
$map[(S 0x00E2,0x20AC,0x0099)] = [string][char]0x2019 # â€™ -> ’
$map[(S 0x00E2,0x20AC,0x2122)] = [string][char]0x2019
$map[(S 0x00E2,0x20AC,0x02DC)] = [string][char]0x2018 # â€˜ -> ‘
$map[(S 0x00E2,0x20AC,0x201C)] = [string][char]0x201C
$map[(S 0x00E2,0x20AC,0x201D)] = [string][char]0x201D
$map[(S 0x00E2,0x20AC,0x201C)] = [string][char]0x201C
$map[(S 0x00E2,0x20AC,0x0093)] = [string][char]0x2013 # en dash
$map[(S 0x00E2,0x20AC,0x0094)] = [string][char]0x2014 # em dash
$map[(S 0x00E2,0x20AC,0x00A6)] = [string][char]0x2026 # ellipsis
$map[(S 0x00E2,0x201A,0x00AC)] = [string][char]0x20AC # euro
$map[(S 0x00C2,0x00A0)] = '&nbsp;'
$map[(S 0x00C3,0x00A9)] = [string][char]0x00E9 # é
$map[(S 0x00C3,0x00AB)] = [string][char]0x00EB # ë
$map[(S 0x00C3,0x00A8)] = [string][char]0x00E8 # è
$map[(S 0x00C3,0x00AF)] = [string][char]0x00EF # ï
$map[(S 0x00C3,0x00B6)] = [string][char]0x00F6 # ö
$map[(S 0x00C3,0x00BC)] = [string][char]0x00FC # ü
$map[(S 0x00C3,0x00A1)] = [string][char]0x00E1 # á
$map[(S 0x00C3,0x00B3)] = [string][char]0x00F3 # ó
$map[(S 0x00C3,0x00BA)] = [string][char]0x00FA # ú
$map[(S 0x00C3,0x00B1)] = [string][char]0x00F1 # ñ
$map[(S 0x00C3,0x00A7)] = [string][char]0x00E7 # ç
$map[(S 0x00C3,0x0089)] = [string][char]0x00C9 # É
$map[(S 0x00C3,0x008B)] = [string][char]0x00CB # Ë
$map[(S 0x00C3,0x009C)] = [string][char]0x00DC # Ü
$map[(S 0x00C3,0x0096)] = [string][char]0x00D6 # Ö
# Two-character fallback: â€ without final byte, seen before a stray box in Chrome.
$map[(S 0x00E2,0x20AC)] = [string][char]0x201D
$files = Get-ChildItem -Recurse -Include *.html,*.json,*.txt -File | Where-Object { $_.FullName -notmatch '\\.git\\' -and $_.FullName -notmatch '\\archief\\le-network\.WordPress' }
$changed = 0
foreach ($file in $files) {
  $text = Get-Content -Raw -LiteralPath $file.FullName -Encoding UTF8
  $new = $text
  foreach ($key in $map.Keys) { $new = $new.Replace($key, $map[$key]) }
  if ($new -ne $text) {
    Set-Content -LiteralPath $file.FullName -Value $new -NoNewline -Encoding UTF8
    $changed++
    "fixed $((Resolve-Path -Relative $file.FullName))"
  }
}
"changed $changed"
