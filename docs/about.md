# About this fork

py-staticmaps has been through three hands, and which one you are installing
matters.

```
flopp/py-staticmaps          the original, by Florian Pigorsch
  └─ lowtower/py-staticmaps     a fork that carried it on
       └─ Jxck-S/py-staticmaps     this repository
```

| | Last commit | On PyPI |
|---|---|---|
| [flopp/py-staticmaps](https://github.com/flopp/py-staticmaps) | April 2024 | yes, as `py-staticmaps` |
| [lowtower/py-staticmaps](https://github.com/lowtower/py-staticmaps) | September 2026 | no |
| [Jxck-S/py-staticmaps](https://github.com/Jxck-S/py-staticmaps) | current | no |

The original stopped at `0.5.0` in April 2024, though that version was not
uploaded to PyPI until April 2026 — so the package is newer than the code in
it. Both forks have carried on since.

## Which one `pip install` gives you

**`pip install py-staticmaps` installs the original**, because that is the
name on PyPI and neither fork publishes under it. That is version `0.5.0`,
whose code dates from April 2024, and it has none of the work described in
these docs.

To install this fork:

```shell
pip install git+https://github.com/Jxck-S/py-staticmaps
```

Or from a clone:

```shell
git clone https://github.com/Jxck-S/py-staticmaps
cd py-staticmaps
pip install .
```

The extras work the same way:

```shell
pip install "py-staticmaps[cairo,pymgl] @ git+https://github.com/Jxck-S/py-staticmaps"
```

## What each layer added

Measured against the original `0.5.0`, and verified by checking each feature
against the source of all three repositories.

### Via lowtower

- `ImageMarker` — place your own PNG on the map
- `Bounds` — take part in framing without drawing
- `set_tighten_to_bounds()` — crop the tiles to the objects
- The bulk of the packaging, linting and CI the project runs on

### In this repository

- [Vector tile providers](providers/vector-tiles.md) — OpenFreeMap, Maptoolkit
  and VersaTiles, rendered through MapLibre Native
- [An api key mechanism](providers/api-keys.md), and providers that refuse to
  render rather than returning a watermarked tile
- [High-DPI output](providers/high-dpi.md) — `pixel_ratio` for vector, `@2x`
  tiles for raster
- [Fractional zoom](rendering/size-and-zoom.md#fractional-zoom) for vector
  providers
- `size` and `logical_size` keywords on the render methods
- [Focused objects](rendering/focus-and-bounds.md#focused-objects), so framing
  can follow one object among many
- An [in-memory tile cache](rendering/caching.md#in-memory-caching) and
  `set_max_min_zoom()`
- [`Point` and `Square`](drawing/markers.md) objects
- This documentation site

## Contributed back upstream

Traffic has not been one way. The fix for
[lines crossing the date line](drawing/lines.md#crossing-the-date-line)
started here:

1. The bug was reported against the original as
   [flopp#37](https://github.com/flopp/py-staticmaps/issues/37), *"Line: Large
   Distance over IDL causes problem"*
2. [FailSpy](https://github.com/FailSpy) fixed it in a pull request against
   **this** repository, merged in February 2024
3. The same branch became
   [flopp#38](https://github.com/flopp/py-staticmaps/pull/38) and was merged
   upstream that April, where the `idl.py` example was added alongside it

So a geodesic line spanning the Pacific renders correctly in all three
repositories, and it is the fork that fixed it. For that reason the date line
fix is **not** listed above as something this fork adds: the original has it
too.

## Licence and credit

MIT throughout, on the same terms at every layer.

- Original work copyright (c) 2020
  [Florian Pigorsch](https://github.com/flopp)
- Fork work by [Lowtower](https://github.com/lowtower) and
  [Jack Sweeney](https://github.com/Jxck-S)

The copyright headers throughout the source still name Florian Pigorsch,
because the bulk of the design is his. A fork inherits the work, not the
authorship.

## Staying in sync

The repository keeps all three as git remotes:

```shell
git remote -v
# origin     https://github.com/Jxck-S/py-staticmaps.git
# lowtower   https://github.com/lowtower/py-staticmaps.git
# upstream   https://github.com/flopp/py-staticmaps.git
```

Which is why changes here try not to alter shared code more than they need
to: a smaller diff against `upstream` and `lowtower` is a smaller merge next
time either of them moves.
