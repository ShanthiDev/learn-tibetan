import { curriculum, item } from './content'
import { lessonMastered, playableItems, unlockedCount, type Progress } from './engine/progress'

/** Derived lesson state shared by Home and Quiz. */
export function pathState(p: Progress, unlockAll: boolean) {
  const lessons = curriculum.lessons
  const unlocked = unlockedCount(p, lessons, item, unlockAll)
  const status = lessons.map((l, i) => ({
    lesson: l,
    unlocked: i < unlocked,
    playable: playableItems(l, item).length > 0,
    mastered: lessonMastered(p, l, item),
  }))
  const current = status.find((s) => s.unlocked && s.playable && !s.mastered) ?? null
  return { unlocked, status, current }
}
