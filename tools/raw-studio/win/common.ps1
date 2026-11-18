# RAW 영상공장 윈도우판 공통 (2026-11-18). install.ps1 / start.ps1 / update.ps1 이 불러 씀
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
Set-Location $Root
$Py = Join-Path $Root ".venv\Scripts\python.exe"
function Refresh-Path {
  # 방금 설치한 프로그램(node·ffmpeg·uv·git·gh)을 이 창에서 바로 쓰게 경로 다시 읽기
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
function Say($m) { Write-Host $m -ForegroundColor Cyan }
function Need($id, $cmd) {
  if (Get-Command $cmd -ErrorAction SilentlyContinue) { return }
  Say "▶ $cmd 설치 ($id)"
  winget install --id $id -e --silent --accept-source-agreements --accept-package-agreements | Out-Host
  Refresh-Path
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "$cmd 설치가 안 됐어요. 창을 닫고 이 파일을 한 번 더 실행해 주세요 (설치 직후엔 새 창에서만 보일 때가 있어요)" }
}
function Pause-End { Write-Host ""; Read-Host "엔터를 누르면 창이 닫혀요" | Out-Null }
