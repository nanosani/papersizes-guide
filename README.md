# papersizes-guide

Official client packages for the [papersizes.guide](https://papersizes.guide/) open paper size dataset: 324 sizes across 23 series, offline, with no dependencies.

Covers ISO A, B and C, US and ANSI, ARCH, envelopes, photo prints, business and ID cards, book trim sizes, newspapers, billboards, and regional standards from Japan, China, France, Canada, Colombia and the British Imperial system.

| Package | Install | Docs |
| --- | --- | --- |
| npm | `npm install papersizes-guide` | [npm/papersizes-guide](npm/papersizes-guide/README.md) |
| PyPI | `pip install papersizes-guide` | [pypi](pypi/README.md) |

```js
const paper = require('papersizes-guide');
paper.get('A4').pixels(300);            // [2480, 3508]
paper.find(8.5, 11, { unit: 'in' })[0]; // Letter
```

```python
import papersizes_guide as paper
paper.get("A4").pixels(300)              # (2480, 3508)
paper.find(8.5, 11, unit="in")[0].size   # Letter
```

## Design

Only millimetre dimensions are stored. Inches, centimetres, points, pixels, aspect ratio, area and sheet weight are all derived on access, so the packages cannot contradict themselves or the site, and adding a resolution costs nothing.

Where two sizes share exact dimensions, such as Letter and ANSI A at 215.9 × 279.4 mm, lookups return the more familiar one first, matching the ranking the website uses.

## Refreshing the data

The bundled dataset is generated from the live API. After any dimension changes upstream:

```bash
python build.py
```

That rewrites `sizes.json` in both packages. Bump both version numbers before publishing.

## Releasing

Both packages publish from a single tag push, using OIDC trusted publishing on
each registry. No tokens are stored in this repository.

```bash
# bump the version in npm/papersizes-guide/package.json and pypi/pyproject.toml,
# then:
git tag v1.0.1 && git push --tags
```

The workflow refuses to publish if the tag does not match the version in the
manifest, and runs a smoke test against the bundled dataset before either
package leaves the runner.


## Live API

The same data is available as a free REST API with no key and open CORS, documented at [papersizes.guide/data](https://papersizes.guide/data/):

```bash
curl "https://papersizes.guide/wp-json/papersizes/v1/size/a4"
curl "https://papersizes.guide/wp-json/papersizes/v1/find?w=8.5&h=11&unit=in"
curl "https://papersizes.guide/wp-json/papersizes/v1/sizes?format=csv"
```

## Where the numbers come from

ISO and ANSI values are generated from the standard formulas rather than transcribed, so they cannot drift. Regional and historical sizes are cross-checked against at least two published references, and any size whose sources disagree carries a note on its page. The process is documented at [papersizes.guide/methodology](https://papersizes.guide/methodology/).

Found a wrong dimension? Open an issue here, or [report it on the site](https://papersizes.guide/contact/). Corrections are published with a note saying what changed.

## Licence

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Use it commercially, modify it, redistribute it. The only condition is credit.

```
PaperSizes.guide paper size dataset, version 2026.09.07.
https://papersizes.guide/data/ — CC BY 4.0
```

The dimensions themselves are published facts drawn from ISO 216, ISO 217, ISO 269, ANSI/ASME Y14.1, JIS P 0138, GB/T 148 and the trade standards named on each size page. Facts are not copyrightable; the licence covers the compilation, the naming and the cross-references.
