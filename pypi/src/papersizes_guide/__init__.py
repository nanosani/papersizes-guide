"""
papersizes-guide — every standard paper size, offline.

Dimensions are stored in millimetres and everything else is derived, so the
package can never disagree with itself about what A4 is.

    >>> import papersizes_guide as paper
    >>> a4 = paper.get("A4")
    >>> a4.width_mm, a4.height_mm
    (210.0, 297.0)
    >>> a4.pixels(300)
    (2480, 3508)
    >>> paper.find(8.5, 11, unit="in")[0].size.name
    'Letter'

Data: https://papersizes.guide/data/ (CC BY 4.0)
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from importlib import resources
from typing import Iterator, Literal, NamedTuple, Sequence

__all__ = [
    "PaperSize",
    "Series",
    "Match",
    "all_sizes",
    "get",
    "find",
    "series",
    "series_list",
    "VERSION",
    "LICENCE",
    "ATTRIBUTION",
    "SOURCE",
]

MM_PER_IN = 25.4
PT_PER_IN = 72
Unit = Literal["mm", "cm", "in", "pt"]
_TO_MM = {"mm": 1.0, "cm": 10.0, "in": MM_PER_IN, "pt": MM_PER_IN / PT_PER_IN}

_RATIOS = [(1, 1), (2, 3), (3, 4), (4, 5), (5, 7), (3, 5), (9, 16), (1, 2),
           (2, 1), (3, 2), (4, 3), (5, 4), (7, 5), (5, 3), (16, 9), (1, 3)]

# Several sizes share exact dimensions (Letter and ANSI A are both 215.9 x 279.4 mm).
# When they tie, prefer the one a person is more likely to have meant, matching the
# ranking papersizes.guide itself uses.
_FAMILIARITY = {
    "a": 5, "us": 5, "b": 4, "c": 4, "iso-envelopes": 4, "us-envelopes": 4,
    "photo": 4, "cards": 3, "ra-sra": 3, "books": 2, "japan": 2, "ansi": 1, "arch": 1,
}


def _ratio_label(w: float, h: float) -> str:
    r = h / w
    if abs(r - math.sqrt(2)) < 0.01:
        return "1:√2"
    for a, b in _RATIOS:
        if abs(r - b / a) < 0.012:
            return f"{a}:{b}"
    return f"1:{round(r, 2)}"


@dataclass(frozen=True)
class PaperSize:
    """One paper size. All derived values are computed from the millimetre dimensions."""

    slug: str
    name: str
    series: str
    series_name: str
    standard: str
    category: str
    region: str
    url: str
    width_mm: float
    height_mm: float
    aliases: Sequence[str] = field(default_factory=tuple)

    # -- derived ---------------------------------------------------------
    @property
    def width_cm(self) -> float:
        return round(self.width_mm / 10, 2)

    @property
    def height_cm(self) -> float:
        return round(self.height_mm / 10, 2)

    @property
    def width_in(self) -> float:
        return round(self.width_mm / MM_PER_IN, 2)

    @property
    def height_in(self) -> float:
        return round(self.height_mm / MM_PER_IN, 2)

    @property
    def width_pt(self) -> float:
        return round(self.width_mm / MM_PER_IN * PT_PER_IN, 1)

    @property
    def height_pt(self) -> float:
        return round(self.height_mm / MM_PER_IN * PT_PER_IN, 1)

    @property
    def ratio(self) -> float:
        return round(self.height_mm / self.width_mm, 4)

    @property
    def ratio_label(self) -> str:
        return _ratio_label(self.width_mm, self.height_mm)

    @property
    def area_mm2(self) -> int:
        return round(self.width_mm * self.height_mm)

    @property
    def area_m2(self) -> float:
        return round(self.width_mm * self.height_mm / 1e6, 4)

    @property
    def diagonal_mm(self) -> float:
        return round(math.hypot(self.width_mm, self.height_mm), 1)

    @property
    def orientation(self) -> str:
        return "portrait" if self.height_mm >= self.width_mm else "landscape"

    def pixels(self, dpi: int = 300) -> tuple[int, int]:
        """Pixel dimensions at a given resolution."""
        return (
            round(self.width_mm / MM_PER_IN * dpi),
            round(self.height_mm / MM_PER_IN * dpi),
        )

    def weight(self, gsm: float) -> float:
        """Weight of one sheet in grams at a given gsm."""
        return round(self.area_m2 * gsm, 3)

    def __str__(self) -> str:
        return f"{self.name} ({self.width_mm:g} × {self.height_mm:g} mm)"


class Series(NamedTuple):
    slug: str
    name: str
    standard: str
    url: str


class Match(NamedTuple):
    size: PaperSize
    diff_mm: float
    rotated: bool


def _load() -> tuple[str, str, str, str, tuple[PaperSize, ...], tuple[Series, ...]]:
    raw = resources.files(__package__).joinpath("data/sizes.json").read_text(encoding="utf-8")
    bundle = json.loads(raw)
    sizes = tuple(
        PaperSize(
            slug=s["slug"],
            name=s["name"],
            series=s["series"],
            series_name=s["series_name"],
            standard=s.get("std") or "",
            category=s.get("cat") or "",
            region=s.get("region") or "",
            url=s["url"],
            width_mm=float(s["width_mm"]),
            height_mm=float(s["height_mm"]),
            aliases=tuple(s.get("aliases") or ()),
        )
        for s in bundle["sizes"]
    )
    series_rows = tuple(
        Series(slug=t["slug"], name=t["name"], standard=t.get("standard", ""), url=t["url"])
        for t in bundle["series"]
    )
    return bundle["version"], bundle["licence"], bundle["attribution"], bundle["source"], sizes, series_rows


VERSION, LICENCE, ATTRIBUTION, SOURCE, _SIZES, _SERIES = _load()
_BY_SLUG = {s.slug: s for s in _SIZES}


def all_sizes() -> tuple[PaperSize, ...]:
    """Every size in the dataset."""
    return _SIZES


def get(name_or_slug: str) -> PaperSize | None:
    """Look up one size by slug, name or alias, case-insensitively."""
    if not name_or_slug:
        return None
    q = str(name_or_slug).strip().lower()
    if q in _BY_SLUG:
        return _BY_SLUG[q]
    for s in _SIZES:
        if s.name.lower() == q:
            return s
    for s in _SIZES:
        if any(a.lower() == q for a in s.aliases):
            return s
    return None


def series(slug: str) -> tuple[PaperSize, ...]:
    """Every size in one series, e.g. series("a")."""
    q = str(slug).lower()
    return tuple(s for s in _SIZES if s.series == q)


def series_list() -> tuple[Series, ...]:
    """The series index."""
    return _SERIES


def _familiarity(size: PaperSize) -> int:
    score = _FAMILIARITY.get(size.series, 0)
    if size.slug in ("letter", "a4"):
        score += 2
    return score


def find(width: float, height: float, unit: Unit = "mm", limit: int = 6) -> list[Match]:
    """
    Identify a sheet from its measurements. Orientation does not matter.

    Returns matches sorted by how far off they are, closest first.
    """
    if unit not in _TO_MM:
        raise ValueError("unit must be one of mm, cm, in, pt")
    factor = _TO_MM[unit]
    w = float(width) * factor
    h = float(height) * factor
    if w <= 0 or h <= 0:
        raise ValueError("width and height must be positive numbers")

    def score(s: PaperSize) -> Match:
        same = abs(s.width_mm - w) + abs(s.height_mm - h)
        turned = abs(s.width_mm - h) + abs(s.height_mm - w)
        return Match(size=s, diff_mm=round(min(same, turned), 2), rotated=turned < same)

    matches = [score(s) for s in _SIZES]
    matches.sort(key=lambda m: (m.diff_mm, -_familiarity(m.size)))
    return matches[:limit]


def __iter__() -> Iterator[PaperSize]:  # pragma: no cover - convenience only
    return iter(_SIZES)
