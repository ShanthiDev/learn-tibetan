// Minimal headless-Chrome driver (CDP over Node's built-in WebSocket) for UI checks without deps.
// Usage: node tools/shot.mjs <url> <out-prefix> [js-step ...]
// Each js-step is evaluated in the page, then a screenshot <out-prefix>-<n>.png is taken.
// A step "click:<css selector>" performs a trusted mouse click (counts as a user gesture).
import { spawn } from 'node:child_process'
import { writeFileSync } from 'node:fs'
import { homedir } from 'node:os'

const [url, out, ...steps] = process.argv.slice(2)
const bin = `${homedir()}/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell`
const port = 9333
const chrome = spawn(bin, ['--no-sandbox', `--remote-debugging-port=${port}`, '--window-size=390,760', '--hide-scrollbars', 'about:blank'])
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
let target
for (let i = 0; i < 50 && !target; i++) {
  await sleep(100)
  try { target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === 'page') } catch {}
}
const ws = new WebSocket(target.webSocketDebuggerUrl)
await new Promise((r) => ws.addEventListener('open', r))
let id = 0
const pending = new Map()
ws.addEventListener('message', (e) => { const m = JSON.parse(e.data); pending.get(m.id)?.(m.result); pending.delete(m.id) })
const send = (method, params = {}) => new Promise((r) => { pending.set(++id, r); ws.send(JSON.stringify({ id, method, params })) })
const shot = async (n) => writeFileSync(`${out}-${n}.png`, Buffer.from((await send('Page.captureScreenshot')).data, 'base64'))

await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 760, deviceScaleFactor: 1, mobile: true })
await send('Page.navigate', { url })
await sleep(1500)
await shot(0)
for (const [i, step] of steps.entries()) {
  let js = step
  if (step.startsWith('click:')) {
    const sel = JSON.stringify(step.slice(6))
    const box = (await send('Runtime.evaluate', { expression: `(() => { const r = document.querySelector(${sel}).getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2] })()`, returnByValue: true })).result.value
    for (const type of ['mousePressed', 'mouseReleased'])
      await send('Input.dispatchMouseEvent', { type, x: box[0], y: box[1], button: 'left', clickCount: 1 })
    js = `'clicked ' + ${sel}`
  }
  const r = await send('Runtime.evaluate', { expression: js, awaitPromise: true, returnByValue: true })
  if (r?.result?.value !== undefined) console.log(`step ${i + 1}:`, JSON.stringify(r.result.value))
  await sleep(250)
  await shot(i + 1)
}
chrome.kill()
process.exit(0)
