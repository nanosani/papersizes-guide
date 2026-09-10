'use strict';

/**
 * papersizes-guide — every standard paper size, offline.
 *
 * Dimensions are stored in millimetres and everything else is derived, so the
 * package can never disagree with itself about what A4 is.
 *
 * Data: https://papersizes.guide/data/ (CC BY 4.0)
 */

const bundle = require('./data/sizes.json');

const MM_PER_IN = 25.4;
const PT_PER_IN = 72;

const round = (n, places) => {
  const f = Math.pow(10, places);
  return Math.round(n * f) / f;
};

/** Nearest simple ratio, matching how the site labels proportions. */
function ratioLabel(w, h) {
  const r = h / w;
  if (Math.abs(r - Math.SQRT2) < 0.01) return '1:√2';
  const pairs = [[1, 1], [2, 3], [3, 4], [4, 5], [5, 7], [3, 5], [9, 16], [1, 2], [2, 1], [3, 2], [4, 3], [5, 4], [7, 5], [5, 3], [16, 9], [1, 3]];
  for (const [a, b] of pairs) {
    if (Math.abs(r - b / a) < 0.012) return a + ':' + b;
  }
  return '1:' + round(r, 2);
}

/** Attach every derived dimension to a stored record. */
function decorate(row) {
  const w = row.width_mm;
  const h = row.height_mm;
  const wIn = w / MM_PER_IN;
  const hIn = h / MM_PER_IN;

  return Object.assign({}, row, {
    widthMm: w,
    heightMm: h,
    widthCm: round(w / 10, 2),
    heightCm: round(h / 10, 2),
    widthIn: round(wIn, 2),
    heightIn: round(hIn, 2),
    widthPt: round(wIn * PT_PER_IN, 1),
    heightPt: round(hIn * PT_PER_IN, 1),
    ratio: round(h / w, 4),
    ratioLabel: ratioLabel(w, h),
    areaMm2: Math.round(w * h),
    areaM2: round((w * h) / 1e6, 4),
    diagonalMm: round(Math.sqrt(w * w + h * h), 1),
    orientation: h >= w ? 'portrait' : 'landscape',

    /** Pixel dimensions at a given resolution, e.g. size.pixels(300) */
    pixels(dpi) {
      const d = Number(dpi) || 300;
      return [Math.round(wIn * d), Math.round(hIn * d)];
    },

    /** Weight of one sheet in grams at a given gsm. */
    weight(gsm) {
      return round(((w * h) / 1e6) * Number(gsm), 3);
    }
  });
}

const SIZES = bundle.sizes.map(decorate);
const BY_SLUG = new Map(SIZES.map((s) => [s.slug, s]));

/** Every size. */
function all() {
  return SIZES.slice();
}

/** One size by slug, or by name / alias, case-insensitively. Null if unknown. */
function get(nameOrSlug) {
  if (!nameOrSlug) return null;
  const q = String(nameOrSlug).trim().toLowerCase();
  const direct = BY_SLUG.get(q);
  if (direct) return direct;
  return (
    SIZES.find((s) => s.name.toLowerCase() === q) ||
    SIZES.find((s) => (s.aliases || []).some((a) => a.toLowerCase() === q)) ||
    null
  );
}

/** Sizes in one series, e.g. series('a'). */
function series(slug) {
  const q = String(slug || '').toLowerCase();
  return SIZES.filter((s) => s.series === q);
}

/** The series list. */
function seriesList() {
  return bundle.series.slice();
}

const TO_MM = { mm: 1, cm: 10, in: MM_PER_IN, pt: MM_PER_IN / PT_PER_IN };

// Several sizes share exact dimensions (Letter and ANSI A are both 215.9 x 279.4 mm).
// When they tie, prefer the one a person is more likely to have meant, matching the
// ranking papersizes.guide itself uses.
const FAMILIARITY = {
  a: 5, us: 5, b: 4, c: 4, 'iso-envelopes': 4, 'us-envelopes': 4,
  photo: 4, cards: 3, 'ra-sra': 3, books: 2, japan: 2, ansi: 1, arch: 1
};

function familiarity(size) {
  let score = FAMILIARITY[size.series] || 0;
  if (size.slug === 'letter' || size.slug === 'a4') score += 2;
  return score;
}

/**
 * Identify a sheet from its measurements. Orientation does not matter.
 * Returns matches sorted by difference, each { size, diffMm, rotated }.
 */
function find(width, height, options) {
  const opts = options || {};
  const factor = TO_MM[opts.unit || 'mm'];
  if (!factor) throw new Error('unit must be one of mm, cm, in, pt');

  const w = Number(width) * factor;
  const h = Number(height) * factor;
  if (!(w > 0 && h > 0)) throw new Error('width and height must be positive numbers');

  const limit = opts.limit || 6;
  return SIZES.map((s) => {
    const same = Math.abs(s.widthMm - w) + Math.abs(s.heightMm - h);
    const turned = Math.abs(s.widthMm - h) + Math.abs(s.heightMm - w);
    return { size: s, diffMm: round(Math.min(same, turned), 2), rotated: turned < same };
  })
    .sort((a, b) => a.diffMm - b.diffMm || familiarity(b.size) - familiarity(a.size))
    .slice(0, limit);
}

module.exports = {
  all,
  get,
  find,
  series,
  seriesList,
  version: bundle.version,
  licence: bundle.licence,
  attribution: bundle.attribution,
  source: bundle.source
};
