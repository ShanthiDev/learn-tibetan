/** Learning tunables. Pedagogy knobs live here, not in the logic. */
export const CONFIG = {
  maxBox: 5,
  masteredBox: 3, // lesson counts as mastered when every new item reaches this box in every mode
  wrongPenalty: 2, // boxes lost on a wrong answer
  retryAfter: [2, 3] as const, // a wrong item returns after this many questions (random in range)
  reviewShare: 0.2, // in a lesson, at most this share of questions comes from earlier lessons
  recentExclude: 2, // do not repeat any of the last N questions (if the pool allows)
  mistakeMemory: 5, // remembered recent mistakes per item/mode
  correctDelayMs: 350, // after a wrong answer the learner continues by button (no timer)
}
