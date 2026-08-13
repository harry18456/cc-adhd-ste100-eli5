English | [繁體中文](README.zh-TW.md)

# adhd-ste100-eli5

A Claude Code **output style** that makes answers cheap to read and cheap to act on.

Not just shorter. Restructured — so the answer is the first thing on screen, every
sentence carries exactly one instruction, and nothing is phrased in a word you have
to stop and decode.

No diagnosis required. Bad days count.

## What changes

**Before**

> Great question! Let me take a look at your authentication setup. Looking at the
> code in `src/auth.ts`, it appears that the token verification logic has been
> implemented using an older version of the jsonwebtoken API, which was deprecated
> in version 9. One approach that could potentially work would be to update the
> package and then refactor that function accordingly. After the changes have been
> made, the auth tests should be run to make sure nothing has been broken. By the
> way, you might also want to think about your dependency versions more broadly at
> some point. Hope this helps! Let me know if you want to dig deeper.

**After**

> Run `npm install jsonwebtoken@latest`.
>
> 1. Open `src/auth.ts`
> 2. Replace `verifyToken` (lines 42 to 58) with the snippet below
> 3. Run `npm test -- auth.spec.ts`
>
> About 10 minutes. The old API stopped working in jsonwebtoken 9. The new API
> returns a promise, so `verifyToken` becomes async.
>
> Skipped: the wider dependency audit. Ask if you want it next.
>
> Next: run step 1. Paste the first failing line if a test fails.

## Why three ingredients

Each one fixes a different layer of friction. They do not overlap, so stacking them
adds coverage instead of repetition.

| Layer | Source | Governs | Sample rule |
|---|---|---|---|
| **1. Message shape** | ADHD support practice | What goes first, what goes last, what gets cut | Restate state every turn — the reader cannot hold "step 3 of 5" between messages |
| **2. Sentence mechanics** | ASD-STE100 controlled English | How each sentence is built | Instructions cap at 20 words, descriptions at 25 |
| **3. Word choice** | ELI5 | Which words go in it | Explain jargon in the same breath, not in a footnote |

Layer 2 is what makes the other two **measurable**. ELI5 says "short sentences";
STE100 says *20 words*. ADHD says "no rambling"; STE100 says *one instruction per
sentence, and no sentence contains "and then" twice*.

### What ASD-STE100 is

A controlled-English standard, first published in 1986 at the request of European
airlines. Their maintenance technicians were mostly non-native English speakers, and
a misread instruction on an aircraft kills people. So the industry wrote a version
of English that cannot be misread: one meaning per word, active voice, simple
tenses, one instruction per sentence, nothing dropped to save space.

The same discipline applies here for the same reason. A tired reader, like a
technician on a tarmac, will not stop to ask what you meant.

("ASD" is the trade association that publishes it — the AeroSpace and Defence
Industries Association of Europe. It is an organization name, not a description.)

## When the layers disagree

Three tie-breakers, and they outrank everything above. They are the part you will
not find upstream.

1. **Cut sentences, not words.**
   Layer 1 wants the message short. Layer 2 forbids dropping the subject or the
   article. Both hold: delete whole sentences that carry no information, and write
   every surviving sentence out in full.

2. **Shorten the path, but never silently.**
   Layer 1 says a short path finished beats a complete path abandoned. Layer 2 says
   never drop a condition or a qualifier without saying so. Both hold: skip the
   step, then name what you skipped in one line.

3. **Restating state is not repetition.**
   Layer 3 wants only what is necessary. Layer 1 wants the state restated every
   turn. The state *is* necessary — it is the reader's working memory, held outside
   their head.

## Language

Language-neutral. The style follows whatever language you write in. Every rule is
about structure and word choice, not about which language you use.

Two rules adapt automatically:

- Sentence caps count characters instead of words for Chinese, Japanese, and Korean
  (about 30 and 40).
- The simple-tense rule is skipped in languages without tense inflection.

## Install

```
/plugin marketplace add harry18456/cc
/plugin install adhd-ste100-eli5@harry18456
```

## Activate

Installing the plugin does **not** turn the style on. Pick it:

```
/config
```

Select **Output style** → **ADHD STE100 ELI5**.

Then run `/clear` or start a new session. An output style is part of the system
prompt, which Claude Code reads once at session start, so it does not take effect
mid-session.

> The standalone `/output-style` command was deprecated in Claude Code v2.1.73 and
> removed in v2.1.91. Use `/config`.

To set it without the menu, put this in `.claude/settings.local.json`:

```json
{
  "outputStyle": "ADHD STE100 ELI5"
}
```

## Scope

Output styles apply to the **main conversation only**. A subagent runs its own
system prompt, so this style does not change how subagents respond. A fork is the
exception, because it inherits the parent's full system prompt.

The style sets `keep-coding-instructions: true`, so Claude Code's built-in software
engineering behavior stays intact. This changes how Claude talks to you. It does not
change how Claude writes code.

## Tune it

Fork, edit `output-styles/adhd-ste100-eli5.md`, and load your copy directly — no
push to GitHub needed:

```
claude --plugin-dir <path to your fork>
```

Common edits:

- Loosen the sentence caps if 20 words feels clipped for your work.
- Drop Layer 1 rule 5 (time estimates) if you find them noise.
- Raise the list cap from 5 if you review long checklists.

## Credits

Layer 1 (message shape) is adapted from
**[ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)** (MIT), which is
itself loosely based on *The Adult ADHD Tool Kit* by J. Russell Ramsay and Anthony
L. Rostain.

Layer 2 (sentence mechanics) is adapted from
**[danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)** (MIT).

Layer 3 (word choice) started as a personal ELI5 output style.

The layer model and the three tie-breaker rules are this project's own.

## License

MIT. See [LICENSE](LICENSE) for third-party notices.

Not affiliated with or endorsed by ASD. Not a medical or diagnostic tool — it shapes
text output, nothing more.
