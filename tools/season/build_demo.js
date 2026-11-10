// 아이패드·태블릿에서 눌러 볼 체험판 (예시 데이터, 비밀번호 1234, 시트에 기록 안 남음)
// node tools/season/build_demo.js → content/2026-11-10_motivation-ideas/raw-season-demo.html (Artifact로 공개)
const fs = require('fs'), path = require('path');
const sample = require('./sample.js');
let h = fs.readFileSync(path.join(__dirname, 'Board.html'), 'utf8');
h = h.replace(/<!doctype html>\s*<html[^>]*>\s*<head>/i, '').replace(/<meta charset="utf-8">/, '').replace(/<meta name="viewport"[^>]*>/, '')
  .replace('<title>RAW SEASON</title>', '<title>RAW SEASON 체험판</title>').replace(/<\/head>\s*<body>/i, '').replace(/<\/body>\s*<\/html>\s*$/i, '');
h = h.replace('html,body{width:100%;height:100%;background:#0e0d12;overflow:hidden}', ':root{color-scheme:dark;padding:0!important}html,body{width:100%;height:100%;background:#0e0d12;overflow:hidden}');
const banner = `<div id="demo" style="position:absolute;left:40px;top:6px;z-index:5;font-family:'Noto Sans KR',sans-serif;font-size:12px;color:#0e0d12;background:#f5be46;border-radius:6px;padding:3px 10px;font-weight:700">체험판 · 예시 학생 · 비밀번호 모두 1234 · 누를 때마다 시계가 35분씩 흘러요 · 새로고침하면 처음으로</div>`;
h = h.replace('<div class="g" id="g1"></div>', banner + '<div class="g" id="g1"></div>');
const mock = `<script>
(() => {
  const S = ${JSON.stringify(sample)};
  let now = S.now; const pad = n => String(n).padStart(2, '0');
  const tick = m => { const d = new Date(now.replace(' ', 'T')); d.setMinutes(d.getMinutes() + m); now = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':00'; };
  const P = x => Date.parse(x.replace(' ', 'T'));
  window.MOCK = {
    get: cb => cb(JSON.parse(JSON.stringify(Object.assign({}, S, { now })))),
    checkIn: (name, pin, kind, note, cb) => setTimeout(() => {
      if (pin !== '1234') return cb({ ok: false, msg: '비밀번호가 달라요' });
      tick(35); const today = now.slice(0, 10), y = new Date(today + 'T00:00:00'); y.setDate(y.getDate() - 1);
      const yest = y.getFullYear() + '-' + pad(y.getMonth() + 1) + '-' + pad(y.getDate());
      const mine = S.log.slice(1).filter(r => r[1] === name && r[0].slice(0, 10) === today).map(r => ({ t: r[0], k: r[2] }));
      const lastT = k => { const a = mine.filter(x => x.k === k); return a.length ? a[a.length - 1].t : ''; };
      const open = (a, b) => lastT(a) > lastT(b);
      const no = msg => cb({ ok: false, msg });
      if (kind === '수업 출석') { const c = mine.filter(x => x.k === '수업 출석'); if (c.length >= 3) return no('수업 출석은 하루 3번까지예요'); if (c.length && (P(now) - P(c[c.length - 1].t)) / 6e4 < 60) return no('방금 수업 출석했어요. 다음 수업 때 눌러요'); }
      if (kind === '운동 완료' || kind === '연습일지') { if (note !== today && note !== yest) return no('오늘이나 어제만 고를 수 있어요');
        if (S.log.some(r => r[1] === name && r[2] === kind && String(r[3] || '').slice(0, 10) === note)) return no((note === today ? '오늘' : '어제') + ' ' + kind + '는 이미 체크했어요'); }
      if (kind === '연습 시작' && open('연습 시작', '연습 끝')) return no('이미 연습 중이에요. 끝나면 [연습 끝]');
      if (kind === '연습 끝' && !open('연습 시작', '연습 끝')) return no('[연습 시작]을 먼저 눌러야 해요');
      S.log.push([now, name, kind, note || '']);
      let msg = '';
      if (kind === '연습 끝') { const min = Math.round((P(now) - P(lastT('연습 시작'))) / 6e4); msg = note === '월말평가 준비' ? '월말평가 준비 ' + min + '분 기록 (점수 없음)' : '개인연습 ' + min + '분' + (min >= 30 ? ' 🔥 인정!' : ' (30분부터 인정)'); }
      if (kind === '운동 완료' || kind === '연습일지') msg = (note === today ? '오늘' : '어제') + ' ' + kind + ' ✓ · 단톡방에 인증 올려 주세요';
      cb({ ok: true, name, kind, time: now.slice(11, 16), msg });
    }, 250)
  };
})();
</script>`;
h = h.replace('<script>\nconst KINDS', mock + '\n<script>\nconst KINDS');
const out = path.join(__dirname, '../../content/2026-11-10_motivation-ideas/raw-season-demo.html');
fs.writeFileSync(out, h); console.log(out, (h.length / 1024).toFixed(0) + 'KB');
