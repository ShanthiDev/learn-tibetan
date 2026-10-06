/** Tiny synthesized feedback sounds (Web Audio, no files): bright up-chime / soft low "bonk". */
let ctx: AudioContext | null = null

function tone(freq: number, start: number, dur: number, type: OscillatorType, gain: number) {
  const c = ctx!
  const osc = c.createOscillator()
  const g = c.createGain()
  osc.type = type
  osc.frequency.setValueAtTime(freq, c.currentTime + start)
  g.gain.setValueAtTime(0, c.currentTime + start)
  g.gain.linearRampToValueAtTime(gain, c.currentTime + start + 0.01)
  g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + start + dur)
  osc.connect(g).connect(c.destination)
  osc.start(c.currentTime + start)
  osc.stop(c.currentTime + start + dur + 0.02)
}

export function sfx(kind: 'correct' | 'wrong', volume: number): void {
  try {
    ctx ??= new AudioContext()
    if (ctx.state === 'suspended') void ctx.resume()
    const v = 0.25 * volume
    if (kind === 'correct') {
      tone(784, 0, 0.12, 'sine', v) // G5
      tone(1175, 0.08, 0.22, 'sine', v) // D6
    } else {
      tone(233, 0, 0.16, 'triangle', v * 1.4) // Bb3
      tone(175, 0.13, 0.28, 'triangle', v * 1.4) // F3
    }
  } catch {
    /* no Web Audio: silent */
  }
}
