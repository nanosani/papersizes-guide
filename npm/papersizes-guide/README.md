# papersizes-guide

Every standard paper size, offline. No network calls, no API key, one dependency-free file.

Covers 324 sizes across 23 series: ISO A, B and C, US and ANSI, ARCH, envelopes, photo prints, business and ID cards, book trim sizes, newspapers, billboards, and regional standards from Japan, China, France, Canada, Colombia and the British Imperial system.

```bash
npm install papersizes-guide
```

## Use

```js
const paper = require('papersizes-guide');

const a4 = paper.get('A4');
a4.widthMm;        // 210
a4.heightIn;       // 11.69
a4.pixels(300);    // [2480, 3508]
a4.ratioLabel;     // '1:√2'
a4.weight(80);     // 4.99  (grams, one sheet at 80 gsm)
```

Look a size up by slug, name or alias:

```js
paper.get('a4');        // slug
paper.get('DIN A4');    // alias
paper.get('No. 10 envelope');
```

Identify a sheet you have measured. Orientation does not matter:

```js
paper.find(8.5, 11, { unit: 'in' })[0].size.name;  // 'Letter'
paper.find(216, 356)[0].size.name;                 // 'Legal'
paper.find(297, 210)[0].rotated;                   // true — that is A4, turned
```

Work with a whole series:

```js
paper.series('a').map((s) => s.name);   // A0 … A10, plus 2A0 and 4A0
paper.seriesList();                     // every series with its governing standard
```

## Why derived, not stored

Only the millimetre dimensions are stored. Inches, points, pixels, ratio, area and sheet weight are all computed on access, so the package cannot contradict itself and adding a resolution costs nothing.

## API

| Call | Returns |
| --- | --- |
| `all()` | Every size |
| `get(nameOrSlug)` | One size, or `null` |
| `find(w, h, { unit, limit })` | Nearest matches, closest first |
| `series(slug)` | Sizes in one series |
| `seriesList()` | The series index |
| `version` | Dataset version, e.g. `2026.09.07` |

Each size exposes `widthMm`, `heightMm`, `widthCm`, `heightCm`, `widthIn`, `heightIn`, `widthPt`, `heightPt`, `ratio`, `ratioLabel`, `areaMm2`, `areaM2`, `diagonalMm`, `orientation`, plus `pixels(dpi)` and `weight(gsm)`. TypeScript definitions are included.

When two sizes share exact dimensions, such as Letter and ANSI A, `find` returns the more familiar one first.

## Data and licence

The dataset comes from [papersizes.guide](https://papersizes.guide/data/) and is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Use it commercially, modify it, redistribute it. The only condition is credit.

ISO and ANSI values are generated from the standard formulas rather than transcribed. Regional and historical sizes are cross-checked against at least two published references, and any size whose sources disagree carries a note on its page. The full process is documented at [papersizes.guide/methodology](https://papersizes.guide/methodology/).

To cite the dataset:

```
PaperSizes.guide paper size dataset, version 2026.09.07.
https://papersizes.guide/data/ — CC BY 4.0
```

A live REST API of the same data, with no key, is documented at [papersizes.guide/data](https://papersizes.guide/data/).

Found an error in a dimension? [Report it](https://papersizes.guide/contact/) and it will be corrected with the correction noted.

Source, and where to report a wrong dimension in code: [github.com/nanosani/papersizes-guide](https://github.com/nanosani/papersizes-guide).
