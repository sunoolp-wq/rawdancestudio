# RAW 영상공장 열기 (윈도우) → 기본 브라우저에 화면. 이 검은 창은 쓰는 동안 켜 두기 (닫으면 멈춤)
. (Join-Path $PSScriptRoot "common.ps1")
Refresh-Path
if (-not (Test-Path $Py)) { Write-Host "먼저 '1_설치하기_윈도우.bat'을 실행해 주세요" -ForegroundColor Red; Pause-End; exit 1 }
$url = "http://127.0.0.1:5577"
try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 $url | Out-Null; Start-Process $url; exit 0 } catch {}
Start-Job -ScriptBlock { Start-Sleep 3; Start-Process "http://127.0.0.1:5577" } | Out-Null
& $Py tools\raw-studio\server.py
Pause-End
