#!/bin/bash
# RAW 영상공장 업데이트: 더블클릭 → Claude가 고친 최신 버전 받기 (처음 한 번은 GitHub 로그인)
# 원장님이 화면에서 바꾼 대강·팝업(tools/daily-story/extra.json)은 합쳐서 보존. 설치물(.venv, node_modules)·결과 영상은 그대로
main() {
  cd "$(dirname "$0")" || exit 1
  set -e
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)"; done
  REPO=sunoolp-wq/rawdancestudio; BR=claude/low-dance-marketing-agents-lisndi
  echo "=== RAW 영상공장 업데이트 ==="
  command -v gh >/dev/null 2>&1 || { echo "▶ GitHub 도구 설치"; brew install gh; }
  if ! gh auth status -h github.com >/dev/null 2>&1; then
    echo "▶ GitHub 로그인 (처음 한 번만). 화면에 나온 8자리 코드를 복사 → 엔터 → 브라우저에서 붙여 넣고 승인"
    gh auth login -h github.com -p https -w
  fi
  gh auth setup-git >/dev/null
  [ -d .git ] || { git init -q; git remote add origin "https://github.com/$REPO.git"; }
  BK=$(mktemp); cp tools/daily-story/extra.json "$BK" 2>/dev/null || echo '{}' > "$BK"
  # 원장님 2026-11-23 "맥 용량" → content(마케팅 기록·사진, 약 600MB)는 맥에 안 받음. 스토리 영상은 만들 때 content 안에 새로 생김
  git sparse-checkout set --no-cone '/*' '!/content/' >/dev/null 2>&1 || true
  echo "▶ 최신 버전 받는 중 (처음엔 몇 분 걸려요)"
  git fetch -q --depth 1 origin "$BR"
  git reset -q --hard FETCH_HEAD
  # 대강·팝업 합치기: 같은 날짜는 원장님 맥에서 바꾼 것이 우선
  python3 - "$BK" tools/daily-story/extra.json <<'PY'
import json, sys
mine = json.load(open(sys.argv[1], encoding="utf-8")); new = json.load(open(sys.argv[2], encoding="utf-8"))
new.update(mine); json.dump(dict(sorted(new.items())), open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
PY
  rm -f "$BK"
  echo "▶ 필요한 프로그램 확인"
  command -v uv >/dev/null 2>&1 || brew install uv
  uv pip install -q --python .venv/bin/python ultralytics lap flask numpy
  npm install --no-audit --no-fund --silent
  chmod +x ./*.command
  echo ""
  echo "✅ 업데이트 끝: $(git log -1 --format='%cd · %s' --date=format:'%m/%d %H:%M' | cut -c1-80)"
  echo "   RAW 영상공장이 켜져 있었다면 검은 창을 닫고 2_RAW영상공장_열기.command를 다시 실행하세요."
}
main "$@"; read -n 1 -s -r -p "아무 키나 누르면 창이 닫혀요"; exit 0
