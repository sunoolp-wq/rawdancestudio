# RAW 영상공장 설치 (윈도우, 처음 한 번만, 10~30분). 1_설치하기_윈도우.bat 이 실행함
. (Join-Path $PSScriptRoot "common.ps1")
try {
  Say "=== RAW 영상공장 설치 (윈도우) ==="
  Get-ChildItem -Path $Root -Recurse -Include *.ps1, *.bat -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue   # 인터넷에서 받은 파일 표시 풀기
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw "winget(앱 설치 관리자)이 없어요. Microsoft Store에서 '앱 설치 관리자(App Installer)'를 설치·업데이트한 뒤 다시 실행해 주세요"
  }
  Refresh-Path
  Need "OpenJS.NodeJS.LTS" "node"
  Need "Gyan.FFmpeg" "ffmpeg"
  Need "astral-sh.uv" "uv"
  Need "Git.Git" "git"
  Need "GitHub.cli" "gh"

  Say "▶ 파이썬 3.12 + 쌤 찾는 AI (YOLO) · 화면 서버"
  if (-not (Test-Path $Py)) { uv venv --python 3.12 --managed-python .venv | Out-Host }
  if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    # 엔비디아 그래픽카드가 있으면 쌤 따라가기를 그래픽카드로 (훨씬 빠름)
    Say "  엔비디아 그래픽카드 확인 → 그래픽카드용 torch"
    uv pip install --python $Py torch torchvision --index-url https://download.pytorch.org/whl/cu124 | Out-Host
  }
  uv pip install --python $Py ultralytics lap flask numpy | Out-Host
  if ($LASTEXITCODE) { throw "파이썬 부품 설치 실패" }

  Say "▶ 자막 만드는 브라우저"
  npm install --no-audit --no-fund | Out-Host
  npx playwright install chromium | Out-Host
  if ($LASTEXITCODE) { throw "브라우저 설치 실패" }

  Say "▶ 글꼴"
  & (Join-Path $PSScriptRoot "fonts.ps1")

  & $Py -c "from ultralytics import YOLO; YOLO('tools/class-reel/yolo11s.pt')" | Out-Null
  Write-Host ""
  Write-Host "✅ 설치 끝! 이제 '2_RAW영상공장_열기_윈도우.bat'을 더블클릭하세요." -ForegroundColor Green
} catch {
  Write-Host ""; Write-Host "❌ $($_.Exception.Message)" -ForegroundColor Red
  Write-Host "   이 화면을 사진 찍어 Claude에게 보내 주세요."
}
Pause-End
