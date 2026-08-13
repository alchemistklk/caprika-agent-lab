#!/usr/bin/env python3
"""Build episode captions (copy into the episode and set ASR/SCRIPT below).

Text comes from SCRIPT.md (the approved narration); timing comes from the
word-level ASR transcript. The two are aligned character by character, because
the ASR mis-hears a few characters (e.g. 截一张图 -> 结一张图) and we must never
ship the ASR's text.
"""
import json, re, difflib, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# --- per-episode configuration -------------------------------------------
ASR  = ROOT/"output/transcribe/<run>/<transcript>-l16.json"   # word-level ASR
SCRIPT_HEADING, SCRIPT_NEXT = "## Part 1", "## Part 2"        # narration section bounds
KEEP = re.compile(r"[一-鿿0-9A-Za-z]")
BREAK_HARD, BREAK_SOFT = "。？！", "，、；：,"
# LINE_CHARS is deliberately unreachable: burned-in cues stay on ONE line so the
# caption band needs a single 54px row, not two.
CUE_CHARS, LINE_CHARS, MIN_DUR, MAX_DUR, TAIL = 26, 999, 0.9, 6.0, 0.08

def script_text():
    body = []
    for line in (ROOT/"SCRIPT.md").read_text().splitlines():
        if line.startswith(SCRIPT_HEADING): body = [];  continue
        if line.startswith(SCRIPT_NEXT): break
        # `**On-screen identifiers:**` wraps onto a continuation line that starts
        # with a backtick — skip those too, or the identifier list lands in the narration
        if body is not None and not line.startswith(("**", "#", "`")) and line.strip():
            body.append(line.strip())
    # SCRIPT.md hard-wraps mid-sentence; join without inserting spaces
    return "".join(body)

def asr_chars():
    words = [w for sg in json.load(open(ASR))["segments"] for w in sg["words"]]
    out = []
    for w in words:
        cs = [c for c in w["word"] if KEEP.match(c)]
        if not cs: continue
        span = (w["end"] - w["start"]) / len(cs)
        for i, c in enumerate(cs):
            out.append((c, w["start"] + i*span, w["start"] + (i+1)*span))
    return out

def main():
    text = script_text()
    idx  = [i for i, c in enumerate(text) if KEEP.match(c)]      # script positions we align
    sc   = "".join(text[i] for i in idx)
    ac   = asr_chars()
    at   = "".join(c for c, _, _ in ac)

    t_start = [None]*len(sc); t_end = [None]*len(sc)
    diffs = []
    sm = difflib.SequenceMatcher(None, sc, at, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2-i1):
                t_start[i1+k], t_end[i1+k] = ac[j1+k][1], ac[j1+k][2]
        else:
            diffs.append((tag, sc[i1:i2], at[j1:j2]))
    # interpolate any script char the ASR did not match
    known = [i for i,v in enumerate(t_start) if v is not None]
    assert known, "alignment failed entirely"
    for i in range(len(sc)):
        if t_start[i] is None:
            prev = max((k for k in known if k < i), default=None)
            nxt  = min((k for k in known if k > i), default=None)
            if prev is None: t_start[i], t_end[i] = t_start[nxt], t_end[nxt]
            elif nxt is None: t_start[i], t_end[i] = t_start[prev], t_end[prev]
            else:
                f = (i-prev)/(nxt-prev)
                t_start[i] = t_end[prev] + f*(t_start[nxt]-t_end[prev])
                t_end[i]   = t_start[i]
    tmap = {p: (t_start[k], t_end[k]) for k, p in enumerate(idx)}   # script pos -> (start,end)

    # ---- segment into cues ----
    # Chinese has no word spaces, so we only ever break at punctuation. A clause
    # that is too long for one line wraps to a second line inside the SAME cue
    # rather than being cut in half, which would split words like 聪|明.
    clauses, buf = [], []
    for p_, ch in enumerate(text):
        buf.append(p_)
        if ch in BREAK_HARD or ch in BREAK_SOFT:
            clauses.append((buf, ch in BREAK_HARD)); buf = []
    if buf: clauses.append((buf, True))

    def span(pos):
        ps = [q for q in pos if q in tmap]
        return (tmap[ps[0]][0], tmap[ps[-1]][1]) if ps else None

    cues, group = [], []
    def flush():
        if not group: return
        pos = [q for cl in group for q in cl]
        sp = span(pos)
        group.clear()
        if not sp: return
        body = "".join(text[q] for q in pos).strip("，、；：, ")
        if not body: return
        if len(body) > LINE_CHARS:                    # wrap, do not split into two cues
            # candidate breaks exclude the final char, or we would emit an empty
            # second line; prefer punctuation near the middle, else the midpoint
            lo, hi = int(len(body)*.3), int(len(body)*.7)
            cands = [i for i, ch in enumerate(body[:-1])
                     if ch in BREAK_SOFT+BREAK_HARD and lo <= i <= hi]
            # if there is no punctuation to break on, keep one long line — a
            # midpoint split would cut a word in half (模|型), which is worse
            if cands:
                cut = min(cands, key=lambda i: abs(i-len(body)/2))
                head, tail = body[:cut+1].rstrip(), body[cut+1:].lstrip()
                if head and tail: body = head + "\n" + tail
        cues.append([sp[0], max(sp[1]+TAIL, sp[0]+MIN_DUR), body])

    for pos, hard in clauses:
        cand = [q for cl in group for q in cl] + pos
        n = sum(1 for q in cand if KEEP.match(text[q]))
        sp = span(cand)
        if group and (n > CUE_CHARS or (sp and sp[1]-sp[0] > MAX_DUR)):
            flush()
        group.append(pos)
        if hard: flush()
    flush()
    for i, c in enumerate(cues):
        if i+1 < len(cues): c[1] = min(c[1], cues[i+1][0] - 0.01)

    def ts(t, sep=","):
        h, m = int(t//3600), int(t%3600//60)
        return f"{h:02d}:{m:02d}:{int(t%60):02d}{sep}{int(round(t%1*1000)):03d}"
    srt = "\n".join(f"{i}\n{ts(s)} --> {ts(e)}\n{b}\n" for i,(s,e,b) in enumerate(cues,1))
    vtt = "WEBVTT\n\n" + "\n".join(f"{ts(s,'.')} --> {ts(e,'.')}\n{b}\n" for s,e,b in cues)
    (ROOT/"captions/episode.srt").write_text(srt, encoding="utf-8")
    (ROOT/"captions/episode.vtt").write_text(vtt, encoding="utf-8")
    json.dump([{"start":round(s,3),"end":round(e,3),"text":b} for s,e,b in cues],
              open(ROOT/"captions/episode.cues.json","w"), ensure_ascii=False, indent=2)

    print(f"cues: {len(cues)}   span: {cues[0][0]:.2f}s → {cues[-1][1]:.2f}s")
    print(f"chars aligned: {sum(1 for v in t_start if v is not None)}/{len(sc)}")
    print("\nASR vs SCRIPT differences (script text wins):")
    for tag, a, b in diffs:
        if a.strip() or b.strip():
            print(f"  {tag:8s} script={a!r}  asr={b!r}")

main()
