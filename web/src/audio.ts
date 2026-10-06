import type { Item } from './content'

/** Static, bundled clips only (no runtime TTS). One cached element per file. */
const cache = new Map<string, HTMLAudioElement>()

export function playItem(it: Item, volume: number): void {
  if (!it.audio) return
  const src = `${import.meta.env.BASE_URL}${it.audio.file}`
  let el = cache.get(src)
  if (!el) {
    el = new Audio(src)
    el.preload = 'auto'
    cache.set(src, el)
  }
  el.volume = volume
  el.currentTime = 0
  el.play().catch(() => {
    /* autoplay blocked until the first user gesture; the play button still works */
  })
}
