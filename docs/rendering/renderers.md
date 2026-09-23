# Renderers

Three renderers, three output types.

```python
context.render_cairo(size=(800, 600)).write_to_png("map.png")
context.render_pillow(size=(800, 600)).save("map.png")

with open("map.svg", "w", encoding="utf-8") as f:
    context.render_svg(size=(800, 600)).write(f, pretty=True)
```

| | Returns | Anti-aliased | Needs |
|---|---|---|---|
| `render_cairo` | `cairo.ImageSurface` | yes | `[cairo]` extra |
| `render_pillow` | `PIL.Image` | no | nothing |
| `render_svg` | `svgwrite.Drawing` | vector output | nothing |

## Which to use

**cairo for anything with curves or diagonals.** Pillow's drawing has no line
joins, caps, dash patterns or anti-aliasing, so a geodesic circle comes out
visibly stepped and a thick polyline notches at every bend. With upright pin
markers only, the difference is close to invisible.

**Pillow when you cannot install cairo** and your objects are simple.

**SVG when the output will be scaled or edited.** It emits real `<path>` and
`<circle>` elements for your objects, so they stay crisp at any size — the
basemap is still an embedded raster image.

Anti-aliasing applies to **your objects only**. The basemap arrives
pre-rendered, whether from raster tiles or from MapLibre, so it looks the same
through all three.

## Performance

Drawing is not the bottleneck. Measured at 1080×1080:

| | Time |
|---|---|
| Raster basemap, warm cache | ~8 ms |
| Vector basemap | ~200 ms |
| 50 markers drawn by cairo | ~1 ms |

cairo is CPU-only — single-threaded software rasterisation, with no GPU
backend available through pycairo. It costs roughly 0.018 ms per object, which
stays negligible into the thousands. At around 15,000 objects on one map it
starts to dominate, and rendering several images in parallel processes is the
practical answer, since cairo is single-threaded.

## Tightening to bounds

SVG only:

```python
context.set_tighten_to_bounds(True)
```

Crops the tiles to the object bounds rather than the full canvas. Not applied
to [vector providers](../providers/vector-tiles.md#limits). See
[Focus and bounds](focus-and-bounds.md).
