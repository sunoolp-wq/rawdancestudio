#!/usr/bin/env bash
# 조각 이어 붙이기 → 자막 얹기 → 원장님 로고 엔딩(본편 끝 1초 디졸브 + 로고 2.5초) → 음악
# 사용: assemble.sh 조각폴더 cues.json 음악.wav 음악시작초 본편끝초 결과.mp4
set -e
CUTS=$1; CUES=$2; MUS=$3; MSS=$4; END=$5; OUT=$6; D=1; E=2.5
DIR=$(cd "$(dirname "$0")" && pwd); W=$(mktemp -d)
ls "$CUTS"/[0-9][0-9].mp4 | sed "s/^/file '/; s/$/'/" > "$W/list.txt"
ffmpeg -nostdin -v error -y -f concat -safe 0 -i "$W/list.txt" -c copy "$W/base.mp4"
node "$DIR/render_titles.js" --video "$W/base.mp4" --cues "$CUES" --out "$W/titled.mp4"
FR=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$W/titled.mp4")
TOT=$(python3 -c "print($END+$E)")   # 본편 마지막 1초 동안 로고로 디졸브 → 로고 2.5초
ffmpeg -nostdin -v error -y -i "$W/titled.mp4" -loop 1 -framerate "$FR" -t "$(python3 -c "print($D+$E)")" -i "$DIR/../class-reel/ending-9x16.png" \
  -ss "$MSS" -t "$TOT" -i "$MUS" -filter_complex \
  "[0:v]trim=0:$END,setpts=PTS-STARTPTS,settb=AVTB,setsar=1,format=yuv420p[a];\
   [1:v]scale=1080:1920,fps=$FR,settb=AVTB,setsar=1,format=yuv420p[b];[a][b]xfade=transition=fade:duration=$D:offset=$(python3 -c "print($END-$D)")[v];\
   [2:a]afade=t=in:st=0:d=0.05,afade=t=out:st=$(python3 -c "print($TOT-2)"):d=2[au]" \
  -map "[v]" -map "[au]" -t "$TOT" -c:v libx264 -crf 15 -preset slow -pix_fmt yuv420p -r "$FR" -c:a aac -b:a 320k -movflags +faststart "$OUT"
rm -rf "$W"; echo "$OUT"
