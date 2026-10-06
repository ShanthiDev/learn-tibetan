import { useEffect, useState } from 'react'

export type Route = 'home' | 'alphabet' | 'settings' | 'learn' | 'practice' | 'review' | 'audio-review'
export type Location = { route: Route; arg?: string }

const parse = (): Location => {
  const [route, arg] = location.hash.replace(/^#\/?/, '').split('/')
  return { route: (route || 'home') as Route, arg }
}

export function useRoute(): Location {
  const [loc, setLoc] = useState<Location>(parse)
  useEffect(() => {
    const on = () => setLoc(parse())
    addEventListener('hashchange', on)
    return () => removeEventListener('hashchange', on)
  }, [])
  return loc
}

export const go = (route: Route, arg?: string) => {
  location.hash = route === 'home' ? '' : `/${route}${arg ? `/${arg}` : ''}`
}
