import { useEffect, useState } from 'react'

export type Route = 'home' | 'alphabet' | 'settings' | 'learn' | 'practice' | 'review' | 'audio-review'

const parse = (): Route => (location.hash.replace(/^#\/?/, '') || 'home') as Route

export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(parse)
  useEffect(() => {
    const on = () => setRoute(parse())
    addEventListener('hashchange', on)
    return () => removeEventListener('hashchange', on)
  }, [])
  return route
}

export const go = (route: Route) => {
  location.hash = route === 'home' ? '' : `/${route}`
}
