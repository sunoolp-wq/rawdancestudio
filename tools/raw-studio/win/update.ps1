# RAW 영상공장 업데이트 (윈도우): Claude가 고친 최신 버전 받기 (처음 한 번은 GitHub 로그인)
# 원장님이 화면에서 바꾼 대강·팝업(tools/daily-story/extra.json)은 합쳐서 보존. 설치물(.venv, node_modules)·결과 영상은 그대로
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
  $bk = [IO.Path]::GetTempFileName()
  if (Test-Path tools\daily-story\extra.json) { Copy-Item tools\daily-story\extra.json $bk -Force } else { Set-Content $bk "{}" -Encoding UTF8 }
  Say "▶ 최신 버전 받는 중 (처음엔 몇 분 걸려요)"
  git sparse-checkout set --no-cone '/*' '!/content/' 2>$null   # content(마케팅 기록, 약 600MB)는 받지 않음 (2026-11-23)
  git -c core.autocrlf=false fetch -q --depth 1 origin $BR; if ($LASTEXITCODE) { throw "받기 실패 (인터넷·로그인 확인)" }
  git -c core.autocrlf=false reset -q --hard FETCH_HEAD
  # 대강·팝업 합치기: 같은 날짜는 원장님 컴퓨터에서 바꾼 것이 우선
  & $Py -c "import json,sys; m=json.load(open(sys.argv[1],encoding='utf-8-sig')); n=json.load(open(sys.argv[2],encoding='utf-8')); n.update(m); json.dump(dict(sorted(n.items())),open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=1)" $bk tools\daily-story\extra.json
  Remove-Item $bk -ErrorAction SilentlyContinue
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
