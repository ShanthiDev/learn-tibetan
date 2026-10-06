import { useRoute } from './router'
import { Alphabet } from './screens/Alphabet'
import { Home } from './screens/Home'
import { SettingsScreen } from './screens/Settings'

export function App() {
  const route = useRoute()
  switch (route) {
    case 'alphabet':
      return <Alphabet />
    case 'settings':
      return <SettingsScreen onReset={() => {}} />
    default:
      return <Home />
  }
}
