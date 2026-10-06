import { useProgress } from './progress'
import { useRoute } from './router'
import { Alphabet } from './screens/Alphabet'
import { Home } from './screens/Home'
import { Quiz } from './screens/Quiz'
import { SettingsScreen } from './screens/Settings'

export function App() {
  const { route, arg } = useRoute()
  const { reset } = useProgress()
  switch (route) {
    case 'alphabet':
      return <Alphabet />
    case 'settings':
      return <SettingsScreen onReset={reset} />
    case 'learn':
      return <Quiz key={`learn-${arg}`} session={{ kind: 'learn', lessonId: arg ?? '' }} />
    case 'practice':
      return <Quiz key="practice" session={{ kind: 'practice' }} />
    case 'review':
      return <Quiz key="review" session={{ kind: 'review' }} />
    default:
      return <Home />
  }
}
