import { go } from '../router'
import { Tib, TopBar } from '../ui'

export function Home() {
  return (
    <div className="screen">
      <TopBar
        back={false}
        title={<Tib>བོད་ཡིག</Tib>}
        right={
          <button className="icon-btn" onClick={() => go('settings')} aria-label="Einstellungen">
            ⚙
          </button>
        }
      />
      <main className="home">
        <button className="btn primary big" onClick={() => go('alphabet')}>
          Alphabet
        </button>
      </main>
    </div>
  )
}
