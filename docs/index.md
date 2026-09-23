# py-staticmaps

Create static map images — PNG or SVG — with markers, geodesic lines, polygons
and circles, from raster or vector tiles.

!!! warning "This is a fork"

    `pip install py-staticmaps` installs
    [the original](https://github.com/flopp/py-staticmaps) from PyPI, which does
    not have the features described here. See [About this fork](about.md) for
    the lineage and how to install this one.

```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)
context.add_object(staticmaps.Marker(staticmaps.create_latlng(48.005, 7.834), color=staticmaps.RED))

context.render_pillow(size=(800, 600)).save("map.png")
```

## What it does

- **Objects** — pin markers, image markers, polylines, polygons and geodesic circles
- **Automatic framing** — the centre and zoom are computed from the objects you added
- **Predefined raster and vector providers**, most needing no api key, and a
  simple way to point at any tile server or MapLibre style of your own
- **Three renderers** — anti-aliased PNG through cairo, plain PNG through Pillow, and real SVG
- **Geodesic geometry** — lines and circles follow the WGS84 ellipsoid, not straight Mercator segments
- **On-disc tile caching**, so repeated renders of the same area cost nothing

## Where to go next

| | |
|---|---|
| [About this fork](about.md) | which py-staticmaps this is |
| [Installation](getting-started/installation.md) | the base package and its extras |
| [Your first map](getting-started/first-map.md) | a map with a marker, end to end |
| [Markers](drawing/markers.md) · [Lines](drawing/lines.md) · [Areas and circles](drawing/areas-and-circles.md) | what you can draw |
| [Choosing a provider](providers/choosing.md) | raster, vector, and which need a key |
| [Examples](examples/index.md) | every example script, with its output |
| [Code reference](reference/index.md) | generated from the docstrings |
