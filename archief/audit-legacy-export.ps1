using namespace System.Net
$ErrorActionPreference='Stop'
$root=(Get-Location).Path
$xml=[xml](Get-Content -Raw archief\le-network.WordPress.2026-07-08.xml)
$items=@($xml.rss.channel.item)
function Get-CData($node,$name){
  $n=$node.SelectSingleNode($name)
  if($null -eq $n){ return '' }
  if($n.'#cdata-section'){ return [string]$n.'#cdata-section' }
  return [string]$n.InnerText
}
function Strip-Html($html){
  if([string]::IsNullOrWhiteSpace($html)){ return '' }
  $s=[WebUtility]::HtmlDecode($html)
  $s=[regex]::Replace($s,'<script[\s\S]*?</script>',' ', 'IgnoreCase')
  $s=[regex]::Replace($s,'<style[\s\S]*?</style>',' ', 'IgnoreCase')
  $s=[regex]::Replace($s,'<[^>]+>',' ')
  $s=[regex]::Replace($s,'\s+',' ').Trim()
  return $s
}
function Normalize($s){
  $s=[WebUtility]::HtmlDecode([string]$s)
  $s=[regex]::Replace($s,'\s+',' ').Trim().ToLowerInvariant()
  return $s
}
function LocalRoute($item){
  $link=[string]$item.link
  $slug=Get-CData $item 'post_name'
  if($link -eq 'https://le-network.nl/' -or $slug -eq 'le-network' -and $link -eq 'https://le-network.nl/'){ return 'index.html' }
  $u=[Uri]$link
  $path=$u.AbsolutePath.Trim('/')
  if([string]::IsNullOrWhiteSpace($path)){ return 'index.html' }
  return (Join-Path $path 'index.html')
}
$published=@($items | Where-Object { (Get-CData $_ 'status') -eq 'publish' -and (Get-CData $_ 'post_type') -in @('page','post') })
$routeRows=@()
$textRows=@()
foreach($item in $published){
  $title=if($item.title.'#cdata-section'){$item.title.'#cdata-section'}else{[string]$item.title}
  $route=LocalRoute $item
  $routePath=Join-Path $root $route
  $exists=Test-Path -LiteralPath $routePath
  $routeRows += [pscustomobject]@{type=(Get-CData $item 'post_type'); slug=(Get-CData $item 'post_name'); title=$title; link=[string]$item.link; local=$route; exists=$exists}
  if($exists){
    $contentNode=$item.SelectSingleNode('content:encoded', (New-Object Xml.XmlNamespaceManager($xml.NameTable)))
  }
}
# namespace manager for content
$ns=New-Object Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace('content','http://purl.org/rss/1.0/modules/content/')
foreach($item in $published){
  $title=if($item.title.'#cdata-section'){$item.title.'#cdata-section'}else{[string]$item.title}
  $route=LocalRoute $item
  $routePath=Join-Path $root $route
  $exists=Test-Path -LiteralPath $routePath
  $sourceText=Strip-Html (($item.SelectSingleNode('content:encoded',$ns)).InnerText)
  if(!$exists -or [string]::IsNullOrWhiteSpace($sourceText)){ continue }
  $localText=Strip-Html (Get-Content -Raw -LiteralPath $routePath)
  $srcNorm=Normalize $sourceText
  $locNorm=Normalize $localText
  $chunks=@()
  $sentences=[regex]::Split($sourceText,'(?<=[.!?])\s+') | Where-Object { $_.Trim().Length -ge 45 } | Select-Object -First 12
  foreach($sentence in $sentences){
    $sn=Normalize $sentence
    if($sn.Length -gt 120){ $sn=$sn.Substring(0,120) }
    $chunks += [pscustomobject]@{snippet=$sentence.Trim(); found=$locNorm.Contains($sn)}
  }
  $missingChunks=@($chunks | Where-Object { -not $_.found })
  $textRows += [pscustomobject]@{slug=(Get-CData $item 'post_name'); title=$title; route=$route; sourceChars=$sourceText.Length; checkedChunks=$chunks.Count; missingChunks=$missingChunks.Count; missingSample=($missingChunks | Select-Object -First 2 | ForEach-Object {$_.snippet}) -join ' || '}
}
# Media paths from attachment_url, _wp_attached_file, and serialized metadata sizes.
$mediaPaths=New-Object System.Collections.Generic.HashSet[string]
foreach($item in $items){
  $attachmentUrl=Get-CData $item 'attachment_url'
  if($attachmentUrl -and $attachmentUrl -match '/wp-content/uploads/(.+)$'){ [void]$mediaPaths.Add($Matches[1]) }
  foreach($pm in @($item.postmeta)){
    $key=Get-CData $pm 'meta_key'; $val=Get-CData $pm 'meta_value'
    if($key -eq '_wp_attached_file' -and $val){ [void]$mediaPaths.Add($val) }
    if($key -eq '_wp_attachment_metadata' -and $val){
      $base=''
      if($val -match 's:4:"file";s:\d+:"([^"]+)"'){ $base=$Matches[1]; [void]$mediaPaths.Add($base) }
      $dir=Split-Path $base -Parent
      foreach($m in [regex]::Matches($val,'s:4:"file";s:\d+:"([^"]+)"')){
        $f=$m.Groups[1].Value
        if($f -match '/'){ [void]$mediaPaths.Add($f) }
        elseif($dir){ [void]$mediaPaths.Add(($dir -replace '\\','/') + '/' + $f) }
      }
    }
  }
}
$mediaRows=@()
foreach($p in ($mediaPaths | Sort-Object)){
  $local=Join-Path $root ('wp-content\uploads\' + ($p -replace '/','\'))
  $mediaRows += [pscustomobject]@{path=$p; exists=(Test-Path -LiteralPath $local); ext=[IO.Path]::GetExtension($p).ToLowerInvariant()}
}
$missingMedia=@($mediaRows | Where-Object { -not $_.exists })
$badLocalLinks = @(rg 'https://(?:i0\.wp\.com/)?le-network\.nl/wp-content/uploads|https://le-network\.nl/wp-content|https://le-network\.nl/wp-includes|^C:\\Users' -n --glob '*.html' --glob '*.css' --glob '*.js' 2>$null)
$report=[pscustomobject]@{
  items=$items.Count
  publishedContent=$published.Count
  attachmentItems=@($items | Where-Object { (Get-CData $_ 'post_type') -eq 'attachment' }).Count
  routesMissing=@($routeRows | Where-Object { -not $_.exists }).Count
  textRowsWithMissingChunks=@($textRows | Where-Object { $_.missingChunks -gt 0 }).Count
  mediaPaths=$mediaRows.Count
  missingMedia=$missingMedia.Count
  videos=@($mediaRows | Where-Object { $_.ext -eq '.mp4' }).Count
  badLocalAssetLinks=$badLocalLinks.Count
}
$routeRows | ConvertTo-Json -Depth 4 | Set-Content archief\audit-routes.json -Encoding UTF8
$textRows | ConvertTo-Json -Depth 4 | Set-Content archief\audit-text.json -Encoding UTF8
$mediaRows | ConvertTo-Json -Depth 4 | Set-Content archief\audit-media.json -Encoding UTF8
$missingMedia | ConvertTo-Json -Depth 4 | Set-Content archief\audit-missing-media.json -Encoding UTF8
$badLocalLinks | Set-Content archief\audit-bad-local-links.txt -Encoding UTF8
$report | ConvertTo-Json -Depth 4
"ROUTE_MISSING"; $routeRows | Where-Object { -not $_.exists } | Format-Table -AutoSize | Out-String
"TEXT_MISSING"; $textRows | Where-Object { $_.missingChunks -gt 0 } | Format-Table slug,route,checkedChunks,missingChunks,missingSample -AutoSize | Out-String
"MISSING_MEDIA_FIRST_30"; $missingMedia | Select-Object -First 30 | Format-Table -AutoSize | Out-String
