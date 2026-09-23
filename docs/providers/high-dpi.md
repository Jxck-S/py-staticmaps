# High-DPI output

Rendering the same map at a higher pixel density, for a HiDPI display or for
print. Raster and vector get there by different routes because their densities
come from different places — but the result is identical.

## The idea

Density is **not** the same as a bigger image, and confusing the two is the
usual mistake.

| | Controls | Doubling it gives you |
|---|---|---|
| Size | how much of the world you see | twice the geographic coverage |
| Density | how finely it is drawn | the same coverage, twice the resolution |

A window analogy: **size is how big the window is; density is the quality of
the glass.**

## Vector: `pixel_ratio`

```python
context.set_tile_provider(staticmaps.tile_provider_OpenFreeMapLiberty)
context.render_cairo(logical_size=(540, 540), pixel_ratio=2)   # -> 1080x1080
context.render_cairo(size=(1080, 1080), pixel_ratio=2)         # -> 1080x1080, same thing
```

`size` is the image you get; `logical_size` is what the ratio is applied to.
See [Size and zoom](../rendering/size-and-zoom.md).

## Raster: `@2x` tiles

Raster density comes from the **provider**, because a denser tile is a
different URL. A provider serving `@2x` tiles declares `tile_size=512`:

```python
provider = staticmaps.tile_provider_CartoVoyager2x
provider.set_api_key("your-key")
context.set_tile_provider(provider)
context.render_cairo(size=(1080, 1080))
```

```python
provider.tile_size()       # 512
provider.pixel_density()   # 2.0
```

`pixel_ratio` is **rejected** for raster providers rather than ignored,
because a raster provider cannot change its tile density on request.

## They are the same trade

These cover identical ground and produce identical dimensions, each with the
provider its comment names:

```python
# with a raster provider whose tile_size is 512
context.render_cairo(size=(1080, 1080))

# with a vector provider
context.render_cairo(logical_size=(540, 540), pixel_ratio=2)
```

Which means the rule is the same for both: **at a fixed output size, doubling
the density halves the coverage.** Switching to a `@2x` provider without
changing the requested size shows you half as much map.

To keep your framing *and* gain the pixels, halve the requested size:

```python
context.render_cairo(size=(540, 540))     # 256px tiles -> 540x540
context.render_cairo(size=(1080, 1080))   # 512px tiles -> 1080x1080, same ground
```

## Object sizes do not scale

Positions scale automatically; `size` and `width` are pixel values and do not.
A `size=12` marker on a 2× map looks half as large as intended, so scale them
yourself:

```python
ratio = 2
context.add_object(staticmaps.Marker(latlng, size=int(12 * ratio)))
context.render_cairo(logical_size=(540, 540), pixel_ratio=ratio)
```

## Choosing a density

Match the label sizing to the size the image will be **seen** at, not its
pixel dimensions. A 1080×1080 image on a phone displays at roughly 400 logical
points — a 2.5× downscale — so labels sized for a 1080px canvas shrink to
roughly 5 px and become unreadable. Labels sized for a 540px canvas survive it.

That is the whole point of a density setting, and why it is worth the halved
coverage.
