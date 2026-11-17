#!/bin/bash
# RAW 영상공장 설치 (맥, 처음 한 번만). 더블클릭 → 안 열리면 오른쪽 클릭 → 열기
cd "$(dirname "$0")"
set -e
export PIP_USE_DEPRECATED=legacy-certs   # 일부 맥에서 pip 인증서 확인(truststore)이 맥 버전을 못 읽어 멈춤 (원장님 맥 2026-11-17)
echo "=== RAW 영상공장 설치 (10~20분 걸려요) ==="
for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)"; done
if ! command -v brew >/dev/null 2>&1; then
  echo "▶ Homebrew(맥 프로그램 설치 도구)를 설치해요. 맥 비밀번호를 물으면 입력하세요 (쳐도 화면에 안 보여요)."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)"; done
fi
echo "▶ 노드 · ffmpeg · uv"
brew install node ffmpeg uv
echo "▶ 쌤 찾는 AI (YOLO) · 화면 서버"
# 파이썬은 uv가 받은 것 사용: macOS 26.2에서 Homebrew python@3.12가 맥 버전을 빈칸으로 읽어 pip·uv가 못 씀 (원장님 맥 2026-11-17)
if ! .venv/bin/python -c "import platform,sys; sys.exit(0 if platform.mac_ver()[0] else 1)" 2>/dev/null; then rm -rf .venv; uv venv --python 3.12 --managed-python .venv; fi
uv pip install --python .venv/bin/python ultralytics lap flask numpy
echo "▶ 자막 만드는 브라우저"
npm install --no-audit --no-fund
npx playwright install chromium
echo "▶ 글꼴"
bash tools/fonts/install.sh
.venv/bin/python -c "from ultralytics import YOLO; YOLO('tools/class-reel/yolo11s.pt')" >/dev/null
echo ""
echo "✅ 설치 끝! 이제 '2_RAW영상공장_열기.command'를 더블클릭하세요."
read -n 1 -s -r -p "아무 키나 누르면 창이 닫혀요"
