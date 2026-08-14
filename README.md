English | [繁體中文](README.zh-TW.md)

# adhd-ste100-eli5

A Claude Code **output style** that makes answers cheap to read and cheap to act on.

Not just shorter. Restructured — so the answer is the first thing on screen, every
sentence carries exactly one instruction, and nothing is phrased in a word you have
to stop and decode.

No diagnosis required. Bad days count.

## What changes

Both blocks below are real `claude -p` output (Sonnet, Claude Code v2.1.229,
August 2026) for the same prompt: a production API that crashes on
`order.customer.id` because some orders have no `customer` field. One run per
condition, no re-rolls. Prompts, raw outputs, and the scoring script live in
[`eval/`](eval/).

**Before — default style.** 316 words of prose. The fix arrives in the second half.

> ## Why it's happening
>
> `order.customer` is `undefined` for some of the documents returned by
> `db.orders.findOne({ orderId })`. This is a data issue, not a code bug per se —
> some orders in the collection just don't have a `customer` field (or it's
> `null`). Common causes:
>
> - **Guest checkouts** — orders placed without a logged-in user never got a
>   `customer` object attached.
> - **Orphaned/soft-deleted users** — the customer record was deleted (e.g. GDPR
>   erasure, account deletion) but the order document wasn't updated or the
>   reference wasn't populated.
>
> *[cut here for the README — two more causes, then four fix options with code.
> Full text: [`eval/outputs/p2-baseline.md`](eval/outputs/p2-baseline.md)]*

**After — this style.** 141 words, quoted in full.

> Add optional chaining and a guard clause in `summary.js:31`.
>
> ```js
> const userId = order.customer?.id;
> if (!userId) {
>   throw new Error(`Order ${order.orderId} has no customer attached`);
> }
> ```
>
> **Cause**: `order.customer` is `undefined` for some documents. `db.orders.findOne`
> returns whatever is stored. Some order records were saved without a `customer`
> field — likely guest checkouts, deleted-user orders, or old records from before
> `customer` was required.
>
> **Steps**:
> 1. Open `/app/src/orders/summary.js`.
> 2. Replace line 31 with the code above.
> 3. Decide what should happen for orders with no customer — throw, skip, or
>    return a fallback summary. The example throws a clear error instead of
>    crashing with `TypeError`.
> 4. Redeploy and check logs for the new "has no customer attached" message. It
>    tells you which orders are missing data.
>
> **Root fix**: query your database for orders where `customer` is missing or
> null. Decide if those records need a data backfill.
>
> Next: run that query against production data to see how many orders are affected.

### Measured

Five prompt types, one run per condition — bug fix, error diagnosis, schema
decision, concept explanation, multi-step how-to:

| Per answer, averaged | Default | Styled |
|---|---|---|
| Prose words | 367 | 176 |
| Sentences over the 20-word cap | 39% | 8% |
| Forbidden opener / closer | 1 of 5 runs | 0 of 5 |
| Ends with one next action | 0 of 5 | 5 of 5 |

One honest miss: rule 5 of Layer 1 (time estimates) fired in 0 of 5 styled runs.
Method and caveats: [`eval/README.md`](eval/README.md).

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

## What was left out, on purpose

Each source contributed one slice. Put this style next to the originals and you
will find gaps. The gaps are deliberate, not sloppy copying. The three that
matter:

**ELI5's analogies.** Real ELI5 explains through analogies and strips jargon until
a five-year-old follows. This style does the opposite: domain terms stay and get
defined once (Layer 2 rule 10), identifiers stay exact (Layer 3 rule 4). An
analogy costs extra words and hides the exact name — for a fried brain that is a
tax, not a discount. The name keeps the source tweet's spirit, not its literal
method.

**The emotional half of ADHD support practice.** Real ADHD support is heavily
emotional work: encouragement, celebration, managing RSD (rejection sensitive
dysphoria — an outsized emotional response to criticism). This style keeps only
the defensive half. Errors are stated flat and blame no one (Layer 1 rule 9), and
"make the win visible" replaces celebration with a concrete fact. Cheerleading
lines are out entirely: they fail Layer 3 rule 1, and a model that cheers slides
into flattery — which is its own cognitive tax.

**STE100's dictionary and minor checks.** The official standard ships a dictionary
of about 900 approved words; its license restricts redistribution, so Layer 3's
"plainest common word" rule stands in for it. The semicolon ban, the
nominalization check, and the phrasal-verb check were also cut: low yield, and
every added rule dilutes how reliably a model follows the rest.

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
  "outputStyle": "adhd-ste100-eli5:ADHD STE100 ELI5"
}
```

The `adhd-ste100-eli5:` prefix is the plugin namespace, and it is required —
tested on v2.1.229, the bare name `ADHD STE100 ELI5` does not resolve when the
style comes from the plugin. The bare name works only for a copy placed directly
in `.claude/output-styles/`.

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

For headless runs, pass the style explicitly:

```
claude -p "..." --plugin-dir <path> \
  --settings '{"outputStyle":"adhd-ste100-eli5:ADHD STE100 ELI5"}'
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

Layer 3 (word choice) is adapted from the `ELI5` output style that
**[Lydia Hallie](https://x.com/lydiahallie)** shared
[on X](https://x.com/lydiahallie/status/2080378470111256907).

The layer model and the three tie-breaker rules are this project's own.

## License

MIT. See [LICENSE](LICENSE) for third-party notices.

Not affiliated with or endorsed by ASD. Not a medical or diagnostic tool — it shapes
text output, nothing more.
