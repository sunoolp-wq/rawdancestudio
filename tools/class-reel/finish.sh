#!/usr/bin/env bash
# 안무 끝에서 학원 로고 엔딩으로 크로스디졸브. 사용: finish.sh 입력.mp4 안무끝초 출력.mp4 [9x16|16x9] [디졸브초=1] [엔딩초=2.5]
set -e
IN=$1; END=$2; OUT=$3; AR=${4:-9x16}; D=${5:-1}; E=${6:-2.5}
DIR=$(cd "$(dirname "$0")" && pwd); IMG=$DIR/ending-$AR.png
read W H FR < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$IN" | tr ',' ' ')
ffmpeg -y -v error -i "$IN" -loop 1 -framerate "$FR" -t "$(python3 -c "print($D+$E)")" -i "$IMG" -filter_complex \
 "[0:v]trim=0:$(python3 -c "print($END+$D)"),setpts=PTS-STARTPTS,fps=$FR,settb=AVTB,setsar=1,format=yuv420p[a];[1:v]scale=$W:$H,fps=$FR,settb=AVTB,setsar=1,format=yuv420p[b];[a][b]xfade=transition=fade:duration=$D:offset=$END[v];\
  [0:a]atrim=0:$(python3 -c "print($END+$D)"),asetpts=PTS-STARTPTS,afade=t=out:st=$END:d=$D,apad=whole_dur=$(python3 -c "print($END+$D+$E)")[au]" \
 -map "[v]" -map "[au]" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart "$OUT"
echo "$OUT"
