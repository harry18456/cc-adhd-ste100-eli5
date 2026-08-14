# Eval

The raw material behind the "What changes" section in the main README. Every
quoted block there is a file in `outputs/`, unedited.

## Method

- Claude Code v2.1.229, `claude -p`, model Sonnet, August 2026.
- One run per prompt per condition. No re-rolls.
- Baseline: `claude -p "$(cat prompts/pN-*.txt)"` with no output style.
- Styled: the same command plus `--settings '{"outputStyle":"ADHD STE100 ELI5"}'`,
  with the style file copied into `.claude/output-styles/` in the working
  directory.
- Both conditions disallowed all tools, so each answer is one shot with no file
  reads.
- Style loading was verified with a probe question ("does your system prompt
  contain a section titled 'Layer 1'..."), not assumed. Probe results:
  - Local copy in `.claude/output-styles/` + bare name `ADHD STE100 ELI5` → loads.
  - Plugin (marketplace install or `--plugin-dir`) + bare name → does **not** load.
  - Plugin + qualified name `adhd-ste100-eli5:ADHD STE100 ELI5` → loads.

## Reproduce

```bash
cd eval
mkdir -p .claude/output-styles
cp ../output-styles/adhd-ste100-eli5.md .claude/output-styles/

p=prompts/p2-error.txt
claude -p "$(cat $p)" --model sonnet \
  --disallowedTools "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,Task,TodoWrite" \
  > outputs/p2-baseline.md
claude -p "$(cat $p)" --model sonnet \
  --settings '{"outputStyle":"ADHD STE100 ELI5"}' \
  --disallowedTools "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,Task,TodoWrite" \
  > outputs/p2-styled.md
python score.py outputs/p2-baseline.md outputs/p2-styled.md
```

## Results — English rounds

| Round | Prompt | Prose words: default → styled | Sentences over 20 words: default → styled |
|---|---|---|---|
| p1 | jwt upgrade bug | 375 → 116 (−69%) | 43% → 0% |
| p2 | production TypeError | 316 → 141 (−55%) | 38% → 7% |
| p3 | JSONB vs table | 311 → 164 (−47%) | 38% → 0% |
| p4 | event-loop explainer | 612 → 290 (−53%) | 35% → 7% |
| p5 | dark-mode how-to | 223 → 171 (−23%) | 42% → 25% |
| **avg** | | **367 → 176 (−52%)** | **39% → 8%** |

Styled runs: 0 of 5 hit a forbidden opener or closer (default: 1 of 5). 5 of 5
end with one next action (default: 0 of 5).

## p7 — blame probe (added in v0.2.0)

Added later to test one rule, not the averages: rule 9's blame-free clause. The
error is in the user's own code (a missing `await`) and the prompt ends with
"what did I do wrong?" — bait for second-person fault wording. One run per
condition, Claude Code v2.1.232, model Sonnet, August 2026.

- Baseline took the bait twice: "you're never awaiting it", "you just never
  unwrapped the result". 171 words, 56% of sentences over the 20-word cap.
- Styled named the actor instead: "the handler never awaits it". Zero
  second-person fault wording. 44 words, 0% over cap.
- A third run with the pre-change style (kept out of `outputs/`) also avoided
  blame. So this round shows the bait is real and the style suppresses it; it
  does not isolate the new clause's contribution. That run also answered in
  Chinese despite the English instruction — user-level global instructions can
  override prompt language in `claude -p` runs.
- Shape misses in the styled run: no numbered steps (L1.2), no explicit
  next-action line (L1.3). Same n=1 variance class as caveat 5.

## Caveats — read before quoting these numbers

1. n=1 per prompt per condition. The direction is stable across all five
   prompts; the exact percentages are not.
2. Word counts exclude code blocks. The sentence splitter is crude: inline code
   inflates word counts, and list items without periods can merge into one
   "sentence". p5-styled's one 32-word "sentence" is such an artifact.
3. Rule L1.5 (time estimates) fired in 0 of 5 styled runs. Strengthen the rule
   or drop it — see "Tune it" in the main README.
4. p1-styled's first line contains a wrong clause ("calls `jwt.sign()`'s
   callback-style overload"). Compression does not prevent hallucination. The
   style shapes form, not truth.
5. p6 (Chinese) is quoted in README.zh-TW.md but is not in the table: the
   scorer counts English words, and the CJK caps count characters. By eye, the
   styled run follows the shape rules, except its first line states the cause
   instead of an action — an L1.1 miss.
6. The quoted rounds were chosen from p1–p6 (p7 came later). Within each round there was no
   re-rolling; every file in `outputs/` is first-roll output.
