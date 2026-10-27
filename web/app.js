'use strict';
const $ = (id) => document.getElementById(id);
const STORE = 'dava-usb-ai.chat.v1';
const SYSTEM = 'Sen DAVA USB AI nomli yordamchisan. Foydalanuvchiga odatda o‘zbek tilida, sodda va aniq javob ber. Agar boshqa til so‘ralsa, o‘sha tilda javob ber. Sen internetga ulanmagansan; yangi ma’lumotni tekshirganingni aytma. Bilmagan ma’lumotingni to‘qima. /no_think';
let messages = [], busy = false, online = false, controller = null, toastTimer;
let nextId = 1;
try {
  const saved = JSON.parse(localStorage.getItem(STORE) || '[]');
  messages = normalize(saved);
} catch { messages = []; }
nextId = messages.reduce((n, m) => Math.max(n, m.id + 1), 1);

function normalize(input) {
  if (!Array.isArray(input) || input.length > 400) throw new Error('Suhbat formati noto‘g‘ri.');
  return input.map((m, i) => {
    if (!m || !['user', 'assistant'].includes(m.role) || typeof m.content !== 'string' || m.content.length > 50000) throw new Error('Xabar formati noto‘g‘ri.');
    return {id: i + 1, role: m.role, content: m.content, error: !!m.error, stopped: !!m.stopped};
  });
}
function persist() {
  try { localStorage.setItem(STORE, JSON.stringify(messages.slice(-400))); }
  catch { toast('Brauzer xotirasi to‘lgan. Suhbatni JSON qilib saqlashingiz mumkin.'); }
}
function toast(text) {
  $('toast').textContent = text;
  $('toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('toast').hidden = true; }, 4200);
}
function notice(text) { $('notice').textContent = text; $('notice').hidden = !text; }
function controls() {
  $('send').disabled = busy || !online || !$('prompt').value.trim();
  $('send').hidden = busy;
  $('stop').hidden = !busy;
  $('new-chat').disabled = busy;
  $('import-chat').disabled = busy;
  $('export-chat').disabled = busy;
  $('prompt').readOnly = busy;
}
function scrollDown() { $('conversation').scrollTop = $('conversation').scrollHeight; }
function copy(text) {
  if (navigator.clipboard) return navigator.clipboard.writeText(text).then(() => toast('Nusxalandi.')).catch(() => toast('Nusxalash uchun matnni belgilang va Ctrl+C bosing.'));
  toast('Matnni belgilang va Ctrl+C bosing.');
}
function renderBody(element, text) {
  element.replaceChildren();
  if (!text) {
    const waiting = document.createElement('span'); waiting.className = 'thinking'; waiting.textContent = 'Javob tayyorlanmoqda…'; element.append(waiting); return;
  }
  const pieces = text.split('```');
  pieces.forEach((piece, index) => {
    if (index % 2 === 0) {
      if (!piece.trim()) return;
      const p = document.createElement('p'); p.textContent = piece.trim(); element.append(p);
    } else {
      const nl = piece.indexOf('\n');
      const language = nl >= 0 ? piece.slice(0, nl).trim().slice(0, 40) : 'kod';
      const code = nl >= 0 ? piece.slice(nl + 1).trimEnd() : piece;
      const box = document.createElement('div'); box.className = 'code-box';
      const header = document.createElement('div'); header.className = 'code-header';
      const label = document.createElement('span'); label.textContent = language || 'kod';
      const button = document.createElement('button'); button.type = 'button'; button.textContent = 'Nusxalash'; button.addEventListener('click', () => copy(code));
      const pre = document.createElement('pre'); const c = document.createElement('code'); c.textContent = code; pre.append(c);
      header.append(label, button); box.append(header, pre); element.append(box);
    }
  });
}
function drawMessage(m) {
  let article = document.getElementById('message-' + m.id);
  if (!article) {
    article = document.createElement('article'); article.id = 'message-' + m.id;
    const label = document.createElement('div'); label.className = 'message-label';
    const avatar = document.createElement('span'); avatar.className = 'avatar'; avatar.textContent = m.role === 'user' ? 'S' : 'D';
    const name = document.createElement('strong'); name.textContent = m.role === 'user' ? 'Siz' : 'DAVA USB AI';
    const meta = document.createElement('span'); meta.className = 'message-time';
    label.append(avatar, name, meta);
    const body = document.createElement('div'); body.className = 'message-body';
    const actions = document.createElement('div'); actions.className = 'message-actions';
    const button = document.createElement('button'); button.className = 'copy-message'; button.type = 'button'; button.textContent = 'Nusxalash'; button.addEventListener('click', () => copy(m.content));
    actions.append(button); article.append(label, body, actions); $('messages').append(article);
  }
  article.className = 'message ' + m.role + (m.error ? ' error' : '');
  article.querySelector('.message-time').textContent = m.stopped ? 'To‘xtatildi' : m.seconds ? m.seconds + ' s' : m.role === 'assistant' ? 'Oflayn' : '';
  renderBody(article.querySelector('.message-body'), m.content);
  article.querySelector('.message-actions').hidden = !m.content;
}
function renderAll() {
  $('messages').replaceChildren();
  $('welcome').hidden = messages.length > 0;
  for (const m of messages) drawMessage(m);
}
async function health() {
  try {
    const response = await fetch('/health', {cache: 'no-store', signal: AbortSignal.timeout(2500)});
    const data = await response.json();
    online = response.ok && data.status === 'ok';
    $('status-text').textContent = online ? 'Oflayn · Tayyor' : 'Model yuklanmoqda';
    $('status').className = 'status' + (online ? ' ready' : '');
  } catch {
    online = false; $('status-text').textContent = 'Server o‘chgan'; $('status').className = 'status error';
  }
  controls();
}
async function post(path, body, signal) {
  const response = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body), signal});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error?.message || 'So‘rov bajarilmadi (' + response.status + ').');
  return data;
}
async function context(signal) {
  const history = messages.filter(m => m.content && !m.error).slice(-21).map(m => ({role: m.role, content: m.content}));
  while (history.length && history[0].role !== 'user') history.shift();
  let shortened = false;
  while (true) {
    const combined = [{role: 'system', content: SYSTEM}, ...history];
    const template = await post('/apply-template', {messages: combined, chat_template_kwargs: {enable_thinking: false}}, signal);
    const tokenized = await post('/tokenize', {content: template.prompt, add_special: true}, signal);
    if (!Array.isArray(tokenized.tokens)) throw new Error('Model tokenizeri javob bermadi.');
    if (tokenized.tokens.length <= 2950) {
      if (shortened || messages.filter(m => m.content && !m.error).length > history.length) notice('Suhbat uzunlashgani uchun modelga oxirgi xabarlar yuborildi. To‘liq suhbat ekranda saqlanadi.');
      return combined;
    }
    if (history.length <= 1) throw new Error('Xabaringiz model oynasiga sig‘mayapti. Uni qisqartirib yoki qismlarga bo‘lib yuboring.');
    history.shift();
    while (history.length > 1 && history[0].role !== 'user') history.shift();
    shortened = true;
  }
}
function friendly(error) {
  const text = error.message || String(error);
  if (/fetch|network|Failed to|Load failed/i.test(text)) return 'AI serveri bilan aloqa uzildi. Boshlash terminali ochiqligini tekshiring.';
  if (/context|exceeds|tokens|too large/i.test(text)) return 'Xabar uzun. Qisqaroq savol bering yoki yangi suhbat oching.';
  return text;
}
async function send(event) {
  event.preventDefault();
  const input = $('prompt').value.trim();
  if (!input || busy || !online) return;
  busy = true; controller = new AbortController(); notice('');
  const user = {id: nextId++, role: 'user', content: input};
  messages.push(user); $('prompt').value = ''; $('welcome').hidden = true; drawMessage(user);
  const answer = {id: nextId++, role: 'assistant', content: ''};
  controls(); drawMessage(answer); scrollDown();
  const started = performance.now(); let lastDraw = 0;
  try {
    const combined = await context(controller.signal);
    messages.push(answer);
    const response = await fetch('/v1/chat/completions', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, signal: controller.signal,
      body: JSON.stringify({model: 'Dava-USB-AI', messages: combined, stream: true, max_tokens: 1024,
        temperature: 0.7, top_p: 0.8, top_k: 20, min_p: 0, presence_penalty: 1.0,
        chat_template_kwargs: {enable_thinking: false}})
    });
    if (!response.ok) { const data = await response.json(); throw new Error(data.error?.message || 'AI xatosi: ' + response.status); }
    if (!response.body) throw new Error('Brauzer oqimli javobni qo‘llamayapti. Firefox yoki Chrome’ni yangilang.');
    const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = '', doneSeen = false, finishReason = '';
    function consume(line) {
      if (!line.startsWith('data:')) return;
      const data = line.slice(5).trim(); if (!data) return;
      if (data === '[DONE]') { doneSeen = true; return; }
      const chunk = JSON.parse(data);
      if (chunk.error) throw new Error(chunk.error.message || 'AI so‘rovi bajarilmadi.');
      const choice = chunk.choices?.[0];
      if (choice?.delta?.content) answer.content += choice.delta.content;
      if (choice?.finish_reason) finishReason = choice.finish_reason;
    }
    while (true) {
      const {value, done} = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, {stream: true});
      const lines = buffer.split('\n'); buffer = lines.pop();
      for (const line of lines) consume(line.trimEnd());
      if (performance.now() - lastDraw > 80) { drawMessage(answer); scrollDown(); lastDraw = performance.now(); }
    }
    buffer += decoder.decode();
    for (const line of buffer.split('\n')) consume(line.trimEnd());
    if (!doneSeen && !finishReason) throw new Error('Javob oxirigacha kelmadi. Terminal ochiqligini tekshiring.');
    if (!answer.content.trim()) throw new Error('Model bo‘sh javob qaytardi. Savolni boshqacha yozing.');
    if (finishReason === 'length') notice('Javob uzunlik chegarasiga yetdi. Davomini olish uchun “Davom et” deb yozing.');
  } catch (error) {
    if (!messages.includes(answer)) messages.push(answer);
    if (error.name === 'AbortError') {
      answer.stopped = true;
      if (!answer.content) { answer.content = 'Javob to‘xtatildi.'; answer.error = true; }
    } else {
      const detail = friendly(error);
      if (answer.content) notice(detail);
      else { answer.content = detail; answer.error = true; }
      $('prompt').value = input;
    }
  } finally {
    answer.seconds = ((performance.now() - started) / 1000).toFixed(1);
    drawMessage(answer); busy = false; controller = null; persist(); controls(); scrollDown(); $('prompt').focus();
  }
}
$('chat-form').addEventListener('submit', send);
$('prompt').addEventListener('input', controls);
$('prompt').addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); if (!busy && online && $('prompt').value.trim()) $('chat-form').requestSubmit(); } });
$('stop').addEventListener('click', () => controller?.abort());
$('new-chat').addEventListener('click', () => {
  if (busy) return;
  if (messages.length && !confirm('Yangi suhbat ochilsinmi? Kerak bo‘lsa, avval joriy suhbatni saqlang.')) return;
  messages = []; nextId = 1; persist(); notice(''); renderAll(); $('prompt').value = ''; controls(); $('prompt').focus();
});
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => { if (busy) return; $('prompt').value = button.dataset.prompt; controls(); $('prompt').focus(); }));
$('help').addEventListener('click', () => $('help-dialog').showModal());
$('close-help').addEventListener('click', () => $('help-dialog').close());
$('export-chat').addEventListener('click', () => {
  if (!messages.length) { toast('Avval suhbatni boshlang.'); return; }
  const data = JSON.stringify({app: 'DAVA USB AI', version: 1, exported: new Date().toISOString(), messages}, null, 2);
  const url = URL.createObjectURL(new Blob([data], {type: 'application/json'}));
  const a = document.createElement('a'); a.href = url; a.download = 'DAVA_suhbat_' + new Date().toISOString().slice(0, 10) + '.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 10000);
});
$('import-chat').addEventListener('click', () => { if (!busy) $('import-file').click(); });
$('import-file').addEventListener('change', async event => {
  const file = event.target.files[0]; if (!file) return;
  try {
    if (file.size > 2 * 1024 * 1024) throw new Error('Suhbat fayli 2 MB dan katta.');
    const data = JSON.parse(await file.text()); const imported = normalize(Array.isArray(data) ? data : data.messages);
    if (messages.length && !confirm('Ochilgan suhbat joriy suhbatning o‘rnini oladi. Davom etilsinmi?')) return;
    messages = imported; nextId = messages.length + 1; persist(); notice(''); renderAll(); scrollDown(); toast('Suhbat ochildi.');
  } catch (error) { toast('Fayl ochilmadi: ' + friendly(error)); }
  finally { event.target.value = ''; }
});
renderAll(); controls(); health(); setInterval(health, 7000);
window.addEventListener('beforeunload', event => { if (busy) { event.preventDefault(); event.returnValue = ''; } });
