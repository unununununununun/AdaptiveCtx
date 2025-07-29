import re, statistics
from typing import List

__all__ = ["preprocess"]

# simple regex tokenizer (whitespace + punctuation)
_TOKEN_RE = re.compile(r"\W+", re.UNICODE)

WINDOW = 4  # neighbours on each side
LEN_THRESH = 6  # if token len deviates more than this, mark anomalous
LINE_NOISE_RATIO = 0.5  # drop line if >50% tokens are anomalous


def _tokenize(line: str) -> List[str]:
    return [t for t in _TOKEN_RE.split(line) if t]


def preprocess(text: str) -> str:
    """Remove noisy lines using simple length-anomaly on Fibonacci-spiral idea.

    Prototype: we don't build real spiral; instead we compute per-token
    length deviation in a sliding window. If more than LINE_NOISE_RATIO
    tokens in a line are anomalous, drop the whole line.
    """
    cleaned_lines = []
    for line in text.splitlines():
        toks = _tokenize(line)
        if not toks:
            continue
        # compute local median lengths
        anomalies = 0
        for i, tok in enumerate(toks):
            start = max(0, i - WINDOW)
            end = min(len(toks), i + WINDOW + 1)
            window_lens = [len(t) for t in toks[start:end]]
            med = statistics.median(window_lens)
            if abs(len(tok) - med) >= LEN_THRESH:
                anomalies += 1
        if anomalies / len(toks) < LINE_NOISE_RATIO:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)