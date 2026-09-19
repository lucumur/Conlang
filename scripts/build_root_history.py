from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LEX = ROOT / "lexico"
REPO = "lucumur/Conlang"
COMMIT_URL = f"https://github.com/{REPO}/commit/"

EXCLUDED = {"index.json", "morphemes.json", "history.json"}


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
    for path in changed:
        p = Path(path)
        if p.suffix != ".json" or p.name in EXCLUDED:
            continue

        current = entries_at(sha, path)
        previous = entries_at(parent, path) if parent else {}
        for root_id in set(current) | set(previous):
            if current.get(root_id) != previous.get(root_id):
                touched.add(root_id)

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
print({"roots_with_history": len(history), "commits_scanned": len(lines)})
