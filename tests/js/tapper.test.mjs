// Behaviour tests for TAPPER_IN_PAGE_SCRIPT. Usage: node tapper.test.mjs <extracted-script.js>
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const code = fs.readFileSync(process.argv[2], 'utf8');
const LIKE = 'https://webcast.tiktok.com/webcast/room/like/?aid=1988&app_name=tiktok_web&msToken=abc&X-Bogus=DFS';
const tick = (ms = 20) => new Promise(r => setTimeout(r, ms));

function makePage() {
  const page = { keydowns: 0, reply: { status: 200, body: { status_code: 0, data: {} } } };
  const win = { onEvent(ev) { if (ev.type === 'keydown' && ev.key === 'l') page.keydowns++; } };
  const node = (parent) => ({
    tagName: 'DIV', parentNode: parent,
    dispatchEvent(ev) { let n = this; while (n) { if (n.onEvent) n.onEvent(ev); n = n.parentNode; } return true; },
  });
  const doc = node(win);
  const player = node(doc);
  doc.body = node(doc); doc.activeElement = doc.body; doc.documentElement = doc;
  doc.querySelector = (sel) => (/live-player|video/.test(sel) ? player : null);
  doc.querySelectorAll = () => [];

  async function fetchImpl() {
    return new Response(JSON.stringify(page.reply.body), { status: page.reply.status, headers: { 'Content-Type': 'application/json' } });
  }
  class FakeXHR {
    constructor() { this.l = {}; this.responseType = ''; }
    open(m, u) { this.u = u; }
    send() { setTimeout(() => { this.status = page.reply.status; this.responseText = JSON.stringify(page.reply.body); (this.l.load || []).forEach(f => f()); }, 1); }
    addEventListener(t, f) { (this.l[t] ||= []).push(f); }
  }
  class KeyboardEvent { constructor(type, init) { this.type = type; Object.assign(this, init); } }

  const ctx = { document: doc, KeyboardEvent, Request, Response, URLSearchParams, FormData, URL, setTimeout, clearTimeout, setInterval, clearInterval, console, JSON, Date, Math };
  ctx.window = ctx; ctx.fetch = fetchImpl; ctx.XMLHttpRequest = FakeXHR;
  vm.createContext(ctx);
  vm.runInContext(code, ctx);
  ctx.__tiktokStopTapper();
  page.ctx = ctx;
  page.stats = () => ctx.__tiktokGetStats();
  page.like = async (count, status_code = 0, extra, httpStatus = 200) => {
    page.reply = { status: httpStatus, body: { status_code, extra } };
    await ctx.fetch(LIKE, { method: 'POST', body: JSON.stringify({ count }) });
    await tick();
  };
  page.taps = (n) => {
    ctx.__tiktokSetTapperEnabled(true);
    for (let i = 1; i < n; i++) ctx.__tiktokTapperWakeup();
    ctx.__tiktokStopTapper();
  };
  return page;
}

async function testSniffer() {
  const page = makePage();
  const { ctx } = page;

  await ctx.fetch(LIKE, { method: 'POST', body: JSON.stringify({ to_uid: '7123', count: 15, room_id: '7456', enter_from: 'live' }) });
  await tick();
  assert.equal(page.stats().verified, 15, 'JSON body count credited');

  await ctx.fetch('https://webcast.tiktok.com/webcast/stats/like_metrics/?count=15', { method: 'POST', body: '{"count":15}' });
  await ctx.fetch('https://webcast.tiktok.com/webcast/room/check_alive/?room_ids=1&like=1');
  await ctx.fetch('https://mon.tiktokv.com/monitor_browser/collect/batch/?webcast/room/like/', { method: 'POST', body: '{"count":15}' });
  await tick();
  assert.equal(page.stats().verified, 15, 'non-like endpoints not credited');

  await ctx.fetch(new Request(LIKE, { method: 'POST', body: JSON.stringify({ count: 7 }) }));
  await tick(100);
  await ctx.fetch(new URL(LIKE), { method: 'POST', body: '{"to_uid":"1","count":3}' });
  await tick();
  assert.equal(page.stats().verified, 25, 'Request and URL inputs credited');

  const x = new ctx.XMLHttpRequest(); x.open('POST', LIKE); x.send('{"count":4}');
  await tick();
  assert.equal(page.stats().verified, 29, 'XHR credited');

  const before = page.keydowns;
  page.taps(1);
  assert.equal(page.keydowns - before, 1, 'exactly one keydown per tap');
}

async function testFrequencyBlock() {
  const page = makePage();
  page.taps(15); await page.like(15);
  assert.equal(page.stats().delivery, 'ok');

  await page.like(15, 4021043, { like_blocked_until_ms: Date.now() + 400 });
  await page.like(3, 4021043, { like_blocked_until_ms: Date.now() + 400 });
  let s = page.stats();
  assert.equal(s.delivery, 'limited');
  assert.equal(s.blockCount, 1, 'second rejection inside the same block is not a new limit');
  assert.equal(s.failed, 18);
  assert.ok(s.blockedRemainingMs > 250 && s.blockedRemainingMs <= 400, 'remaining ' + s.blockedRemainingMs);

  const d = s.dispatched, k = page.keydowns;
  page.ctx.__tiktokTapperWakeup(); page.ctx.__tiktokTapperBurst(3);
  assert.equal(page.stats().dispatched, d, 'no taps while blocked');
  assert.equal(page.keydowns, k);

  await tick(450);
  s = page.stats();
  assert.equal(s.delivery, 'ok', 'expired block is not reported as rejected');
  assert.ok(s.limitedSeconds >= 0 && s.limitedSeconds <= 1);

  await page.like(2, 4021043, { like_blocked_until_ms: Date.now() + 2600 });
  s = page.stats();
  assert.equal(s.blockCount, 2, 'block after expiry counts as a new limit');
  assert.equal(s.limitedSeconds, 3, 'limited time accumulates');

  await page.like(1, 4021043);  // missing timestamp falls back to 5s instead of NaN
  assert.ok(page.stats().blockedRemainingMs > 4500);
}

async function testRejectedAndUnconfirmed() {
  const page = makePage();
  page.taps(15); await page.like(15);

  await tick(100); await page.like(15, 10011);
  assert.equal(page.stats().delivery, 'rejected');
  assert.equal(page.stats().lastRejectStatus, 10011);
  await page.like(15, 0, undefined, 500);
  assert.equal(page.stats().lastRejectStatus, 'HTTP 500');
  await tick(100); await page.like(15);
  assert.equal(page.stats().delivery, 'ok');

  page.taps(30); assert.equal(page.stats().delivery, 'ok');
  page.taps(1); assert.equal(page.stats().delivery, 'unconfirmed');
  assert.equal(page.stats().unconfirmedTaps, 31);
  await tick(100); await page.like(15);
  assert.equal(page.stats().delivery, 'ok');
}

async function testBurstFirstTapIsImmediate() {
  const page = makePage();
  page.ctx.__tiktokSetTapperEnabled(true);
  page.ctx.__tiktokTapperBurst(3);
  // The initial loop tap plus the burst's first tap run synchronously, without waiting on timers
  assert.equal(page.stats().dispatched, 2);
  page.ctx.__tiktokStopTapper();
}

await testSniffer();
await testFrequencyBlock();
await testRejectedAndUnconfirmed();
await testBurstFirstTapIsImmediate();
console.log('tapper JS tests passed');
process.exit(0);
