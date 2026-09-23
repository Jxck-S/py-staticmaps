# Size and zoom

## Asking for a size

```python
context.render_cairo(size=(1080, 1080))                        # the image you get
context.render_cairo(logical_size=(540, 540), pixel_ratio=2)   # -> 1080x1080
context.render_cairo(size=(1080, 1080), pixel_ratio=2)         # -> 1080x1080
```

`size` is the resulting image. `logical_size` is what the
[pixel ratio](../providers/high-dpi.md) is applied to. They are mutually
exclusive.

The last two need a **vector** provider. A `pixel_ratio` passed explicitly for
a raster provider raises, because a raster provider cannot change its tile
density on request — it gets density from
[`@2x` tiles](../providers/high-dpi.md#raster-2x-tiles) instead. So with a
raster provider, `size` is simply the image you get.

## Automatic framing

With no centre or zoom set, both are computed from the objects:

```python
context.add_object(staticmaps.Marker(a))
context.add_object(staticmaps.Marker(b))
context.render_pillow(size=(800, 600))    # framed around a and b
```

Fix either or both:

```python
context.set_center(staticmaps.create_latlng(37.799, -122.400))
context.set_zoom(14)
context.reset_center_zoom()    # go back to automatic
```

You can ask what it decided:

```python
center, zoom = context.determine_center_zoom(800, 600)
```

## Fractional zoom

Raster tiles exist only at whole zoom levels, so fitting to your objects has
to step *down* to the next whole level — wasting up to almost a factor of two
of usable scale.

A vector style renders at any scale, so it fits exactly:

| | Raster | Vector |
|---|---|---|
| Auto-fit, same objects | `16` | `16.468` |
| `set_zoom(18.5)` | tiles exist only at 18 and 19 | renders at 18.5 |

```python
context.set_zoom(16.47)   # vector providers
```

Vector also stays sharp well past the zoom its data is published at, because
geometry is rescaled rather than pixels: OpenFreeMap's data stops at zoom 14
and still renders crisply at 18 and beyond.

## Constraining the automatic zoom

```python
context.set_max_min_zoom(max_zoom=16, min_zoom=12)
```

Bounds only the *computed* zoom, not one you set explicitly. It matters when
rendering a sequence of images over moving objects, where an unconstrained
zoom jumps between frames. When a bound binds, the objects are no longer
guaranteed to fit.

Separately, every provider caps its own maximum; the effective zoom is the
tighter of the two.
