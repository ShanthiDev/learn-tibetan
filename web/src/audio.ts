import { clipOf, type Item, type Variant } from './content'

/** Static, bundled clips only (no runtime TTS). One cached element per file. */
const cache = new Map<string, HTMLAudioElement>()

export function playItem(it: Item, volume: number, variant: Variant = 'A'): void {
  const clip = clipOf(it, variant)
  if (clip) playFile(clip.file, volume)
}

/** `file` is relative to web/public and carries a content hash (?v=…), so replaced clips reload. */
export function playFile(file: string, volume: number): void {
  const src = `${import.meta.env.BASE_URL}${file}`
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
