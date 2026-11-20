"""Builds index.json from the directory's files, and checks every contribution.

Each contribution is a file and what it says about itself:
    components/<id>.ocpc + components/<id>.json
    tables/<Name>.csv    + tables/<Name>.json
Run:  python build_index.py          (writes index.json)
      python build_index.py --check  (only checks, for pull requests)
"""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 16 * 1024 * 1024
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]{0,80}$")
KINDS = {"components": ("Component", ".ocpc"), "tables": ("Table", ".csv")}


def check_component(path, item):
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if names - {"component.json", "worksheet.ocp"}:
            raise ValueError("holds files other than component.json and worksheet.ocp")
        spec = json.loads(archive.read("component.json"))
    if spec.get("id") != item["id"]:
        raise ValueError(f"its id is {spec.get('id')!r}, not {item['id']!r}")
    if int(spec.get("version", 1)) != int(item["version"]):
        raise ValueError("its version differs from its .json")


def check_table(path):
    text = path.read_bytes()
    try:
        text = text.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = text.decode("latin-1")
    if len([line for line in text.splitlines() if line.strip()]) < 2:
        raise ValueError("needs a heading row and at least one row")


def build():
    items, problems = [], []
    for folder, (kind, extension) in KINDS.items():
        for meta in sorted((ROOT / folder).glob("*.json")):
            name = meta.stem
            try:
                if not ID.match(name):
                    raise ValueError("its name may hold only letters, digits, - and _")
                item = json.loads(meta.read_text(encoding="utf-8"))
                data = ROOT / folder / (name + extension)
                if not data.is_file():
                    raise ValueError(f"{data.name} is missing")
                size = data.stat().st_size
                if not 0 < size <= MAX_BYTES:
                    raise ValueError("the file is empty or larger than 16 MB")
                if item.get("id") != name or item.get("kind") != kind:
                    raise ValueError("its id or kind does not match its file")
                for field in ("title", "category", "description", "author"):
                    if not isinstance(item.get(field), str):
                        raise ValueError(f"it has no {field}")
                (check_component(data, item) if kind == "Component" else check_table(data))
                items.append({
                    "kind": kind, "id": name, "title": item["title"][:100], "category": item["category"][:60],
                    "description": item["description"][:2000], "version": int(item.get("version", 1)),
                    "author": item["author"][:60], "file": f"{folder}/{data.name}", "size": size,
                    "sha256": hashlib.sha256(data.read_bytes()).hexdigest(), "published": item.get("published"),
                })
            except (ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as error:
                problems.append(f"{folder}/{name}: {error}")
    return items, problems


if __name__ == "__main__":
    items, problems = build()
    for problem in problems:
        print("Problem:", problem)
    if "--check" in sys.argv:
        sys.exit(1 if problems else 0)
    (ROOT / "index.json").write_text(json.dumps({"version": 1, "items": items}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"index.json: {len(items)} items")
