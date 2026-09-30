/* Browser side only: read input, call Flask, show results. */
const $ = s => document.querySelector(s);
let chatId = null, busy = false, controller = null;
const SUGGEST = [
  ['💡 Project idea', 'Give me 5 final year project ideas in machine learning with datasets'],
  ['🧱 Full-stack plan', 'Full stack project plan: placement portal using React, Node.js and MongoDB. Folder structure, database, APIs and build steps'],
  ['🇮🇳 Hinglish', 'Mujhe Flask me login system kaise banana hai, step by step samjhao'],
  ['🗺️ Roadmap', 'Make an 8 week roadmap for a Flask + SQLite AI chatbot project'],
  ['🎤 Viva prep', 'What questions can be asked in viva for a RAG chatbot project?'],
  ['🧠 हिंदी में', 'मुझे RAG क्या होता है आसान भाषा में समझाओ']
];

/* ---------- intro splash (once per browser session) ---------- */
(function intro(){
  const el = $('#intro'); if (!el) return;
  if (sessionStorage.getItem('introSeen')) { el.remove(); return; }
  sessionStorage.setItem('introSeen', '1');
  const steps = [...el.querySelectorAll('.steps span')];
  steps.forEach((s, i) => setTimeout(() => s.classList.add('on'), 350 + i * 420));
  const close = () => { el.classList.add('out'); setTimeout(() => el.remove(), 800); };
  el.onclick = close; setTimeout(close, 3000);
})();

/* ---------- markdown (escape first, then format) ---------- */
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function inline(s){ return s.replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>'); }
function md(text){
  const out = []; let list = null, code = null;
  const close = () => { if (list) { out.push(`</${list}>`); list = null; } };
  for (const raw of esc(text).split('\n')) {
    if (raw.trim().startsWith('```')) {
      if (code === null) { close(); code = []; } else { out.push('<pre><code>' + code.join('\n') + '</code></pre>'); code = null; }
      continue;
    }
    if (code !== null) { code.push(raw); continue; }
    let m;
    if ((m = raw.match(/^#{1,4}\s+(.*)/))) { close(); out.push('<h4>' + inline(m[1]) + '</h4>'); }
    else if ((m = raw.match(/^\s*[-*•]\s+(.*)/))) { if (list !== 'ul') { close(); out.push('<ul>'); list = 'ul'; } out.push('<li>' + inline(m[1]) + '</li>'); }
    else if ((m = raw.match(/^\s*\d+[.)]\s+(.*)/))) { if (list !== 'ol') { close(); out.push('<ol>'); list = 'ol'; } out.push('<li>' + inline(m[1]) + '</li>'); }
    else if (raw.trim()) { close(); out.push('<p>' + inline(raw) + '</p>'); }
    else close();
  }
  close(); if (code !== null) out.push('<pre><code>' + code.join('\n') + '</code></pre>');
  return out.join('');
}
function plain(text){ return text.replace(/```[\s\S]*?```/g, ' code block ').replace(/[*#`•]/g, ''); }

/* ---------- API helper ---------- */
async function api(url, opts = {}) {
  const r = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts });
  if (r.status === 401) { location.href = '/login'; throw new Error('login'); }
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Something went wrong');
  return data;
}

/* ---------- messages ---------- */
function scrollDown(){ const m = $('#msgs'); m.scrollTop = m.scrollHeight; }
function makeMsg(role){
  const wrap = document.createElement('div'); wrap.className = 'msg ' + (role === 'user' ? 'user' : 'ai');
  wrap.innerHTML = `<div class="av">${role === 'user' ? 'You' : 'AI'}</div><div class="bubble"></div>`;
  $('#thread').appendChild(wrap);
  return { wrap, bubble: wrap.querySelector('.bubble') };
}
function addUser(text){ const m = makeMsg('user'); m.bubble.innerHTML = md(text); scrollDown(); }

/* action row under every AI answer: sources, copy, speak, thumbs, regenerate (last answer only) */
function renderActions(m, text, sources, messageId, feedback){
  m.bubble.querySelector('.acts')?.remove();
  const acts = document.createElement('div'); acts.className = 'acts';
  acts.innerHTML = (sources || []).map(s => `<span class="chip" title="${esc(s.file)}">📚 ${esc(s.title)}</span>`).join('');
  const add = (label, title, fn, cls = '') => {
    const b = document.createElement('button'); b.className = 'act ' + cls; b.textContent = label; b.title = title; b.onclick = () => fn(b);
    acts.appendChild(b); return b;
  };
  add('Copy', 'Copy answer', b => { navigator.clipboard.writeText(text); b.textContent = 'Copied ✓'; setTimeout(() => b.textContent = 'Copy', 1400); });
  add('🔊', 'Read aloud', () => speak(text));
  if (messageId) {
    const up = add('👍', 'Good answer', () => rate(1)), down = add('👎', 'Bad answer', () => rate(-1));
    let cur = feedback || 0; const paint = () => { up.classList.toggle('sel', cur === 1); down.classList.toggle('sel', cur === -1); }; paint();
    async function rate(v){
      const next = cur === v ? 0 : v;
      try { await api('/api/feedback', { method: 'POST', body: JSON.stringify({ message_id: messageId, value: next }) }); cur = next; paint(); } catch (e) {}
    }
  }
  document.querySelectorAll('.regen').forEach(b => b.remove());          // only the newest answer can be regenerated
  add('🔄 Regenerate', 'Answer again', () => regenerate(), 'regen');
  m.bubble.appendChild(acts);
}
function addAI(text, sources, messageId, feedback){ const m = makeMsg('ai'); m.bubble.innerHTML = md(text); renderActions(m, text, sources, messageId, feedback); return m; }

function showWelcome(){
  $('#thread').innerHTML = `<div class="welcome"><div class="orb big" style="margin:0 auto 18px"></div>
    <h2>What are we <span class="grad-text">building</span> today?</h2>
    <div class="muted">Ask in English, Hindi or Hinglish. Type, or tap 🎤 and speak.</div>
    <div class="sugg">${SUGGEST.map(([t, q]) => `<button data-q="${esc(q)}"><b>${t}</b><small>${esc(q)}</small></button>`).join('')}</div></div>`;
  document.querySelectorAll('.sugg button').forEach(b => b.onclick = () => { $('#inp').value = b.dataset.q; sendChat(); });
}

/* ---------- streaming ---------- */
function setBusy(v){
  busy = v; const b = $('#send');
  b.textContent = v ? '■ Stop' : 'Send ➤'; b.classList.toggle('stop', v);
}
function onSend(){ if (busy) { controller && controller.abort(); } else sendChat(); }

async function streamAnswer(payload){
  const m = makeMsg('ai'); m.bubble.innerHTML = '<span class="typing"><i></i><i></i><i></i></span>';
  setBusy(true); controller = new AbortController(); scrollDown();
  let full = '', sources = [], messageId = null, started = false, pending = false;
  const paint = () => { pending = false; m.bubble.innerHTML = md(full); m.bubble.classList.add('cursor'); scrollDown(); };
  try {
    const r = await fetch('/api/chat/stream', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: controller.signal });
    if (r.status === 401) { location.href = '/login'; return; }
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || 'Something went wrong');
    const reader = r.body.getReader(), dec = new TextDecoder(); let buf = '';
    while (true) {
      const { value, done } = await reader.read(); if (done) break;
      buf += dec.decode(value, { stream: true });
      let i; while ((i = buf.indexOf('\n\n')) >= 0) {
        const line = buf.slice(0, i).trim(); buf = buf.slice(i + 2);
        if (!line.startsWith('data:')) continue;
        const ev = JSON.parse(line.slice(5));
        if (ev.type === 'meta') { chatId = ev.chat_id; sources = ev.sources; }
        else if (ev.type === 'token') { started = true; full += ev.text; if (!pending) { pending = true; requestAnimationFrame(paint); } }
        else if (ev.type === 'done') messageId = ev.message_id;
        else if (ev.type === 'error' && !started) full = '⚠️ ' + ev.message;
      }
    }
  } catch (e) {
    if (e.name !== 'AbortError') full = full || '⚠️ ' + e.message;
  }
  m.bubble.classList.remove('cursor');
  if (full.trim()) { m.bubble.innerHTML = md(full); renderActions(m, full, sources, messageId, 0); }
  else m.wrap.remove();
  setBusy(false); controller = null; scrollDown(); loadHistory();
  if (chatId && !messageId && full.trim()) reloadIds();       // stopped early: fetch real id so 👍/👎 work
}
async function reloadIds(){
  try { const d = await api('/api/chats/' + chatId); const last = d.messages[d.messages.length - 1];
    if (last && last.role === 'assistant') { const wraps = document.querySelectorAll('.msg.ai'); const w = wraps[wraps.length - 1];
      renderActions({ bubble: w.querySelector('.bubble') }, last.content, last.sources, last.id, last.feedback); } } catch (e) {}
}
async function sendChat(){
  const inp = $('#inp'), text = inp.value.trim(); if (!text || busy) return;
  if (listening) rec.stop();
  inp.value = ''; inp.style.height = 'auto';
  if (!chatId) $('#thread').innerHTML = '';
  addUser(text);
  await streamAnswer({ message: text, chat_id: chatId });
  inp.focus();
}
async function regenerate(){
  if (busy || !chatId) return;
  const last = [...document.querySelectorAll('.msg.ai')].pop(); if (last) last.remove();
  await streamAnswer({ chat_id: chatId, regenerate: true });
}

/* ---------- history ---------- */
function newChat(){ if (busy) return; chatId = null; showWelcome(); document.querySelectorAll('.it').forEach(i => i.classList.remove('on')); switchView('chat'); $('#inp').focus(); }
async function loadHistory(){
  const list = await api('/api/chats?q=' + encodeURIComponent($('#q').value));
  $('#hist').innerHTML = list.length ? '' : '<div class="empty" style="padding:8px">No chats yet. Ask your first question!</div>';
  list.forEach(c => {
    const it = document.createElement('div'); it.className = 'it' + (c.id === chatId ? ' on' : '');
    it.innerHTML = `<span title="${esc(c.title)}">💬 ${esc(c.title)}</span><button title="Delete">✕</button>`;
    it.onclick = () => openChat(c.id);
    it.querySelector('button').onclick = async e => { e.stopPropagation(); if (confirm('Delete this chat?')) { await api('/api/chats/' + c.id, { method: 'DELETE' }); if (chatId === c.id) newChat(); loadHistory(); } };
    $('#hist').appendChild(it);
  });
}
async function openChat(id){
  if (busy) return;
  const d = await api('/api/chats/' + id); chatId = id; switchView('chat'); $('#thread').innerHTML = '';
  d.messages.forEach(m => m.role === 'user' ? addUser(m.content) : addAI(m.content, m.sources, m.id, m.feedback));
  loadHistory(); scrollDown();
}
let st; function searchHistory(){ clearTimeout(st); st = setTimeout(loadHistory, 250); }

/* ---------- create artifact ---------- */
async function createArtifact(){
  const prompt = $('#gp').value.trim(), btn = $('#gbtn'), res = $('#gres'); if (prompt.length < 5) return;
  btn.disabled = true; btn.textContent = 'Generating…'; res.innerHTML = '<div class="typing"><i></i><i></i><i></i></div>';
  try {
    const d = await api('/api/generate', { method: 'POST', body: JSON.stringify({ prompt, format: $('#gf').value }) });
    res.innerHTML = `<div class="card"><b>✅ Your file is ready</b><pre>${esc(d.preview)}</pre>
      <a class="btn primary" href="${d.url}">⬇ Download ${d.file.split('.').pop().toUpperCase()}</a></div>`;
  } catch (e) { res.innerHTML = `<div class="flash error">${esc(e.message)}</div>`; }
  btn.disabled = false; btn.textContent = 'Generate file';
}

/* ---------- VOICE INPUT (Web Speech API) ---------- */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let rec = null, listening = false, voiceBase = '';
function vstat(msg){ $('#vstat').textContent = msg; }
function toggleMic(){
  if (!SR) return;
  if (listening) { rec.stop(); return; }
  const [lang] = $('#vlang').value.split('|');
  rec = new SR(); rec.lang = lang; rec.interimResults = true; rec.continuous = false; rec.maxAlternatives = 1;
  voiceBase = $('#inp').value.trim();
  rec.onstart = () => { listening = true; $('#mic').classList.add('on'); vstat('🔴 Listening… speak now'); };
  rec.onresult = e => {
    let t = ''; for (let i = 0; i < e.results.length; i++) t += e.results[i][0].transcript;
    const inp = $('#inp'); inp.value = (voiceBase ? voiceBase + ' ' : '') + t.trim();
    inp.style.height = 'auto'; inp.style.height = Math.min(inp.scrollHeight, 150) + 'px';
  };
  rec.onerror = e => {
    const msg = { 'not-allowed': 'Microphone blocked. Click the 🔒 in the address bar and allow the microphone.',
      'service-not-allowed': 'Microphone blocked. Allow it in browser settings.',
      'no-speech': 'Did not hear anything. Tap 🎤 and try again.',
      'network': 'Voice needs internet (Chrome sends the audio to Google to convert it to text).',
      'audio-capture': 'No microphone found.' }[e.error] || 'Voice error: ' + e.error;
    vstat('⚠️ ' + msg);
  };
  rec.onend = () => {
    listening = false; $('#mic').classList.remove('on');
    if ($('#vstat').textContent.startsWith('🔴')) vstat('Enter to send · Shift+Enter for a new line');
    if ($('#vauto').checked && $('#inp').value.trim() && $('#inp').value.trim() !== voiceBase) sendChat();
  };
  try { rec.start(); } catch (e) {}
}
function speak(text){                      // read answer aloud (browser text-to-speech)
  if (!('speechSynthesis' in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(plain(text).slice(0, 1800));
  u.lang = /[\u0900-\u097F]/.test(text) ? 'hi-IN' : 'en-IN'; speechSynthesis.speak(u);
}
(function initVoice(){
  if (!SR) { $('#mic').style.display = 'none'; $('#vopts').style.display = 'none'; vstat('Voice input works in Chrome or Edge. Enter to send · Shift+Enter for a new line'); return; }
  const saved = localStorage.getItem('vlang'); if (saved) $('#vlang').value = saved;
  $('#vlang').onchange = () => localStorage.setItem('vlang', $('#vlang').value);
})();

/* ---------- tabs, model status, input ---------- */
function switchView(v){
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('on', t.dataset.v === v));
  document.querySelectorAll('.view').forEach(x => x.classList.toggle('on', x.id === 'v-' + v));
}
document.querySelectorAll('.tab').forEach(t => t.onclick = () => switchView(t.dataset.v));
async function pollStatus(){
  try {
    const d = await api('/api/status'), m = d.model;
    $('#dot').className = 'dot ' + (m.status === 'ready' ? 'ready' : m.status === 'error' ? 'error' : '');
    $('#mstat').textContent = m.status === 'ready' ? 'Ready · ' + d.rag.chunks + ' knowledge chunks'
      : m.status === 'error' ? 'Model offline (using knowledge only)' : m.message;
    setTimeout(pollStatus, m.status === 'ready' || m.status === 'error' ? 30000 : 3000);
  } catch (e) {}
}
const inp = $('#inp');
inp.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); } });
inp.addEventListener('input', () => { inp.style.height = 'auto'; inp.style.height = Math.min(inp.scrollHeight, 150) + 'px'; });
showWelcome(); loadHistory(); pollStatus();
