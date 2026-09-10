"""
Refresh the dataset bundled with the npm and PyPI packages.

Pulls from the live API and writes a compact core record into both packages.
Derived values (inches, points, pixels, ratio, area) are deliberately NOT stored:
the packages compute them from the millimetre dimensions, exactly as the site does,
so the two can never disagree.

    python packages/build.py
"""

import json
import pathlib
import urllib.request

API = "https://papersizes.guide/wp-json/papersizes/v1"
HERE = pathlib.Path(__file__).parent
TARGETS = [
    HERE / "npm" / "papersizes-guide" / "data" / "sizes.json",
    HERE / "pypi" / "src" / "papersizes_guide" / "data" / "sizes.json",
]

KEEP = ("slug", "name", "series", "series_name", "std", "aliases", "url", "cat", "region")


def fetch(path: str) -> dict:
    req = urllib.request.Request(path, headers={"User-Agent": "papersizes-guide-build"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main() -> None:
    sizes = fetch(f"{API}/sizes?fields=full")
    series = fetch(f"{API}/series")

    rows = []
    for s in sizes["sizes"]:
        row = {k: s.get(k) for k in KEEP}
        row["width_mm"] = s["width_mm"]
        row["height_mm"] = s["height_mm"]
        rows.append(row)

    bundle = {
        "version": sizes["version"],
        "licence": sizes["licence"],
        "attribution": sizes["attribution"],
        "source": sizes["source"],
        "series": [
            {"slug": t["slug"], "name": t["name"], "standard": t.get("standard", ""), "url": t["url"]}
            for t in series["series"]
        ],
        "sizes": rows,
    }

    payload = json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
    for target in TARGETS:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
        print(f"wrote {len(payload):,} bytes to {target}")

    print(f"dataset version {bundle['version']}: {len(rows)} sizes, {len(bundle['series'])} series")


if __name__ == "__main__":
    main()
