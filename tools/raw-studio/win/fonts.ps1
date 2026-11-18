# 글꼴 설치 (윈도우 사용자 글꼴 폴더 + 등록). 맥·리눅스의 tools/fonts/install.sh 와 같은 글꼴. 이미 있으면 건너뜀
$Dir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"; New-Item -ItemType Directory -Force -Path $Dir | Out-Null
$Reg = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
function Register($file, $name) {
  $type = if ($file -like "*.otf") { "OpenType" } else { "TrueType" }
  New-ItemProperty -Path $Reg -Name "$name ($type)" -Value (Join-Path $Dir $file) -PropertyType String -Force | Out-Null
}
function Get-Font($family, $w, $file) {
  $dst = Join-Path $Dir $file
  if ((Test-Path $dst) -and (Get-Item $dst).Length -gt 0) { return }
  try {
    # 구글 글꼴: 브라우저가 아닌 프로그램으로 물어보면 ttf 주소를 줌
    $css = (Invoke-WebRequest -UseBasicParsing -UserAgent "curl/8.0" -TimeoutSec 20 "https://fonts.googleapis.com/css2?family=$($family):wght@$w&display=swap").Content
    $url = [regex]::Match($css, "https://fonts\.gstatic\.com[^)]*").Value
    if ($url) { Invoke-WebRequest -UseBasicParsing -TimeoutSec 60 -OutFile $dst $url; Register $file "$($family.Replace('+',' ')) $w"; Write-Host "  설치: $file" }
  } catch { Write-Host "  (건너뜀: $file — $($_.Exception.Message))" }
}
foreach ($w in 300, 400, 500, 700, 900) { Get-Font "Noto+Sans+KR" $w "NotoSansKR-$w.ttf" }
foreach ($w in 500, 600, 700, 800) { Get-Font "Montserrat" $w "Montserrat-$w.ttf" }
Get-Font "Anton" 400 "Anton.ttf"; Get-Font "Bebas+Neue" 400 "BebasNeue.ttf"; Get-Font "Black+Han+Sans" 400 "BlackHanSans.ttf"
# 원장님 글꼴 (GoGo Poster 2020: TRACKPAD 자막용)
Get-ChildItem (Join-Path $PSScriptRoot "..\..\fonts\private\*.otf") -ErrorAction SilentlyContinue | ForEach-Object {
  $dst = Join-Path $Dir $_.Name
  if (-not (Test-Path $dst)) { Copy-Item $_.FullName $dst; Register $_.Name $_.BaseName; Write-Host "  설치: $($_.Name)" }
}
