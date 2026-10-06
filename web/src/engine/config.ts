/** Learning tunables. Pedagogy knobs live here, not in the logic. */
export const CONFIG = {
  maxBox: 5,
  masteredBox: 3, // lesson counts as mastered when every new item reaches this box in every mode
  wrongPenalty: 2, // boxes lost on a wrong answer
  retryAfter: [2, 3] as const, // a wrong item returns after this many questions (random in range)
  newWeight: 2, // weight multiplier for the current lesson's items
  recentExclude: 2, // do not repeat any of the last N questions (if the pool allows)
  mistakeMemory: 5, // remembered recent mistakes per item/mode
  correctDelayMs: 350,
  wrongDelayMs: 1500,
}
