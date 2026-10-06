import { CHAPTERS, curriculum, item } from '../content'
import { lessonScore } from '../engine/progress'
import { difficultCount } from '../engine/select'
import { pathState } from '../lessons'
import { useProgress } from '../progress'
import { go } from '../router'
import { useSettings } from '../settings'
import { Tib, TopBar } from '../ui'

type Status = ReturnType<typeof pathState>['status'][number]

function LessonButton({ s, label }: { s: Status; label: string }) {
  const { progress } = useProgress()
  const [settings] = useSettings()
  const { current } = pathState(progress, settings.unlockAll)
  const score = lessonScore(progress, s.lesson, item)
  const open = s.unlocked && s.playable
  return (
    <button
      className={`lesson ${current?.lesson.id === s.lesson.id ? 'current' : ''} ${s.mastered ? 'mastered' : ''}`}
      disabled={!open}
      onClick={() => go('learn', s.lesson.id)}
      aria-label={`${s.lesson.titleDe}${s.mastered ? ', gemeistert' : open ? '' : ', gesperrt'}`}
    >
      <span className="lesson-label">
        {!open && s.playable && <Lock />}
        {s.mastered && '✓ '}
        {label}
      </span>
      <span className="meter">
        <span style={{ width: `${score * 100}%` }} />
      </span>
    </button>
  )
}

const Lock = () => (
  <svg width="10" height="12" viewBox="0 0 10 12" aria-hidden className="lock">
    <rect x="1" y="5" width="8" height="6.5" rx="1.2" fill="currentColor" />
    <path d="M2.8 5V3.6a2.2 2.2 0 0 1 4.4 0V5" fill="none" stroke="currentColor" strokeWidth="1.4" />
  </svg>
)

export function Home() {
  const { progress } = useProgress()
  const [settings] = useSettings()
  const { unlocked, status, current } = pathState(progress, settings.unlockAll)
  const difficult = difficultCount(progress, curriculum, unlocked, item)
  const started = progress.counter > 0

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
        {current ? (
          <button className="btn primary big continue" onClick={() => go('learn', current.lesson.id)}>
            <span>{started ? 'Weiterlernen' : 'Loslegen'}</span>
            <small>{current.lesson.titleDe}</small>
          </button>
        ) : (
          <p className="note">Alle verfügbaren Lektionen gemeistert. 🙏</p>
        )}
        <div className="btn-row">
          <button className="btn" disabled={!started} onClick={() => go('practice')}>
            Alles üben
          </button>
          <button className="btn" disabled={!difficult} onClick={() => go('review')}>
            Schwieriges{difficult ? ` (${difficult})` : ''}
          </button>
        </div>
        <button className="btn" onClick={() => go('alphabet')}>
          Alphabet <Tib>ཀ་ཁ་ག་ང་</Tib>
        </button>

        <nav className="path" aria-label="Lernpfad">
          <h2>
            <span className="ch-num">2·3</span> Konsonanten lesen
          </h2>
          <ul>
            {curriculum.groups.map((g, r) => {
              const pair = status.filter((s) => s.lesson.id.startsWith(`r${r + 1}-`))
              return (
                <li key={g.id} className="row-path">
                  <span className="row-label">
                    <Tib>{g.itemIds.map((id) => item(id).tibetan).join(' ')}</Tib>
                    <small>{g.labelDe}</small>
                  </span>
                  {pair.map((s) => (
                    <LessonButton key={s.lesson.id} s={s} label={s.lesson.modes[0] === 'tib-wylie' ? 'ཀ → ka' : 'ka → ཀ'} />
                  ))}
                </li>
              )
            })}
          </ul>
          {[4, 5].map((ch) => (
            <section key={ch}>
              <h2>
                <span className="ch-num">{ch}</span> {CHAPTERS[ch]}
              </h2>
              <ul>
                {status
                  .filter((s) => s.lesson.chapter === ch)
                  .map((s) => (
                    <li key={s.lesson.id} className="row-path">
                      <span className="row-label">{s.lesson.titleDe.replace(/^(Vokale|Hören): /, '')}</span>
                      <LessonButton s={s} label={s.playable ? 'üben' : 'Audio folgt'} />
                    </li>
                  ))}
              </ul>
            </section>
          ))}
        </nav>
      </main>
    </div>
  )
}
