from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LEX = ROOT / "lexico"
REPO = "lucumur/Conlang"
COMMIT_URL = f"https://github.com/{REPO}/commit/"

EXCLUDED = {"index.json", "morphemes.json", "history.json", "history-items.json"}


def git(*args, check=True):
    p = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and p.returncode:
        raise RuntimeError(p.stderr.strip() or "git command failed")
    return p.stdout


def json_at(ref, path):
    p = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if p.returncode:
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return None


def words_of(entries):
    """id de vocablo -> (raíz, contenido): mover un vocablo de raíz también cuenta como cambio."""
    out = {}
    for root_id, e in entries.items():
        for w in e.get("words", []) or []:
            if w.get("id"):
                out[w["id"]] = (root_id, w)
    return out


def morphemes_at(ref):
    data = json_at(ref, "lexico/morphemes.json") if ref else None
    return {m["id"]: m for m in (data or {}).get("morphemes", []) if m.get("id")}


def entries_at(ref, path):
    p = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if p.returncode:
        return {}
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        return {}
    return {e["id"]: e for e in data.get("entries", []) if e.get("id")}


history = {}
word_history = {}
morph_history = {}
lines = git(
    "log",
    "--reverse",
    "--format=%H%x1f%cI%x1f%s",
    "--",
    "lexico",
).splitlines()

for line in lines:
    if not line:
        continue
    sha, date, message = line.split("\x1f", 2)
    parent = git("rev-parse", f"{sha}^", check=False).strip()
    changed = git(
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-only",
        "-r",
        sha,
        "--",
        "lexico",
    ).splitlines()

    touched = set()
    touched_words = set()
    touched_morphs = set()
    for path in changed:
        p = Path(path)
        if p.name == "morphemes.json":
            cur_m, prev_m = morphemes_at(sha), morphemes_at(parent)
            touched_morphs |= {i for i in set(cur_m) | set(prev_m) if cur_m.get(i) != prev_m.get(i)}
            continue
        if p.suffix != ".json" or p.name in EXCLUDED:
            continue

        current = entries_at(sha, path)
        previous = entries_at(parent, path) if parent else {}
        for root_id in set(current) | set(previous):
            if current.get(root_id) != previous.get(root_id):
                touched.add(root_id)
        cur_w, prev_w = words_of(current), words_of(previous)
        touched_words |= {i for i in set(cur_w) | set(prev_w) if cur_w.get(i) != prev_w.get(i)}

    item = {"sha": sha, "date": date, "message": message, "url": COMMIT_URL + sha}
    for wid in sorted(touched_words):
        word_history.setdefault(wid, []).append(item)
    for mid in sorted(touched_morphs):
        morph_history.setdefault(mid, []).append(item)

    for root_id in sorted(touched):
        history.setdefault(root_id, []).append(
            {
                "sha": sha,
                "date": date,
                "message": message,
                "url": COMMIT_URL + sha,
            }
        )

payload = {
    "schema_version": 1,
    "repository": REPO,
    "roots": history,
}
(LEX / "history.json").write_text(
    json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)
(LEX / "history-items.json").write_text(
    json.dumps({"schema_version": 1, "repository": REPO, "words": word_history, "morphemes": morph_history},
               ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)
print({"roots_with_history": len(history), "words_with_history": len(word_history),
       "morphemes_with_history": len(morph_history), "commits_scanned": len(lines)})
