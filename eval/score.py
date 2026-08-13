"""Score a Claude Code response against the adhd-ste100-eli5 rules."""
import re
import sys

FORBIDDEN_OPENERS = [
    "great question", "let me", "i'll ", "sure!", "looking at your",
    "here's what", "here is what", "i'd be happy",
]
FORBIDDEN_CLOSERS = [
    "let me know if", "hope this helps", "feel free to ask",
    "anything else", "happy to dig",
]
TIME_HINT = re.compile(
    r"\b(\d+\s*(?:to\s*\d+\s*)?(?:second|minute|hour|day)s?|an afternoon)\b", re.I
)
ACTIONABLE = re.compile(r"`[^`]+`")


def strip_code_blocks(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def sentences(prose):
    parts = re.split(r"(?<=[.!?])\s+", prose)
    return [s.strip() for s in parts if len(s.strip()) > 2]


def score(path):
    raw = open(path, encoding="utf-8").read().strip()
    prose = strip_code_blocks(raw)
    lines = [l for l in raw.splitlines() if l.strip()]
    first, last = lines[0], lines[-1]
    sents = sentences(prose)
    long20 = [s for s in sents if len(s.split()) > 20]
    long25 = [s for s in sents if len(s.split()) > 25]

    print(f"=== {path} ===")
    print(f"chars                    {len(raw)}")
    print(f"words                    {len(prose.split())}")
    print(f"sentences (prose only)   {len(sents)}")
    print(f"  over 20 words          {len(long20)}  ({len(long20)/max(len(sents),1):.0%})")
    print(f"  over 25 words          {len(long25)}  ({len(long25)/max(len(sents),1):.0%})")
    print(f"  longest sentence       {max((len(s.split()) for s in sents), default=0)} words")
    hits_open = [p for p in FORBIDDEN_OPENERS if first.lower().startswith(p) or p in first.lower()[:40]]
    hits_close = [p for p in FORBIDDEN_CLOSERS if p in last.lower()]
    print(f"L1.10 forbidden opener   {'HIT ' + str(hits_open) if hits_open else 'clean'}")
    print(f"L1.10 forbidden closer   {'HIT ' + str(hits_close) if hits_close else 'clean'}")
    print(f"L1.1  action in line 1   {'yes' if ACTIONABLE.search(first) else 'NO'}")
    print(f"L1.2  numbered steps     {'yes' if re.search(r'^\s*1\.', raw, re.M) else 'NO'}")
    next_ok = re.search(r"\bnext\b", last, re.I) or re.search(
        r"^\W*(Run|Open|Paste|Tell|Try|Check|Start|Add)\b", last
    )
    print(f"L1.3  single next action {'yes' if next_ok else 'NO'}")
    print(f"L1.5  time estimate      {'yes' if TIME_HINT.search(prose) else 'NO'}")
    print(f"TB.2  names what skipped {'yes' if re.search(r'\bskipp?e?d?\b', prose, re.I) else 'NO'}")
    print()


for p in sys.argv[1:]:
    score(p)
