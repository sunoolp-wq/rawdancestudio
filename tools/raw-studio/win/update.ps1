# RAW 영상공장 업데이트 (윈도우): Claude가 고친 최신 버전 받기 (처음 한 번은 GitHub 로그인)
# 대강·팝업(tools/daily-story/extra.json)은 클라우드(GitHub) 것을 그대로 씀 (원장님 2026-11-23 "대강은 클라우드에서만 고칠게"). 설치물(.venv, node_modules)·결과 영상은 그대로
. (Join-Path $PSScriptRoot "common.ps1")
$REPO = "sunoolp-wq/rawdancestudio"; $BR = "claude/low-dance-marketing-agents-lisndi"
try {
  Say "=== RAW 영상공장 업데이트 (윈도우) ==="
  Refresh-Path
  Need "Git.Git" "git"; Need "GitHub.cli" "gh"
  gh auth status -h github.com 2>$null | Out-Null
  if ($LASTEXITCODE) {
    Say "▶ GitHub 로그인 (처음 한 번만). 화면에 나온 8자리 코드를 복사 → 엔터 → 브라우저에서 붙여 넣고 승인"
    gh auth login -h github.com -p https -w
  }
  gh auth setup-git | Out-Null
  if (-not (Test-Path .git)) { git init -q; git remote add origin "https://github.com/$REPO.git" }
  Say "▶ 최신 버전 받는 중 (처음엔 몇 분 걸려요)"
  git -c core.autocrlf=false fetch -q --depth 1 origin $BR; if ($LASTEXITCODE) { throw "받기 실패 (인터넷·로그인 확인)" }
  git -c core.autocrlf=false reset -q --hard FETCH_HEAD
  # content(마케팅 기록, 약 600MB)는 받지 않음 (2026-11-23). tools\raw-studio\keep-content.txt 에 적은 폴더만 남김
  $keep = @(); if (Test-Path tools\raw-studio\keep-content.txt) { $keep = @(Get-Content tools\raw-studio\keep-content.txt -Encoding UTF8 | ForEach-Object { ($_ -replace '#.*', '').Trim() } | Where-Object { $_ } | ForEach-Object { "/content/$_/" }) }
  git sparse-checkout set --no-cone '/*' '!/content/' @keep 2>$null
  Say "▶ 필요한 프로그램 확인"
  uv pip install -q --python $Py ultralytics lap flask numpy | Out-Host
  npm install --no-audit --no-fund --silent | Out-Host
  Write-Host ""
  Write-Host ("✅ 업데이트 끝: " + (git log -1 --format="%cd · %s" --date=format:"%m/%d %H:%M")) -ForegroundColor Green
  Write-Host "   RAW 영상공장이 켜져 있었다면 검은 창을 닫고 2_RAW영상공장_열기_윈도우.bat을 다시 실행하세요."
} catch {
  Write-Host ""; Write-Host "❌ $($_.Exception.Message)" -ForegroundColor Red; Write-Host "   이 화면을 사진 찍어 Claude에게 보내 주세요."
}
Pause-End
