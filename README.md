[![CI](https://github.com/Jxck-S/py-staticmaps/workflows/CI/badge.svg)](https://github.com/Jxck-S/py-staticmaps/actions?query=workflow%3ACI)
[![Docs](https://github.com/Jxck-S/py-staticmaps/workflows/Docs/badge.svg)](https://jxck-s.github.io/py-staticmaps/)
[![PyPI Package](https://img.shields.io/pypi/v/py-staticmaps.svg)](https://pypi.org/project/py-staticmaps/)
[![Format](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg?style=flat)](LICENSE)

# py-staticmaps

Create static map images — PNG or SVG — with markers, geodesic lines, polygons
and circles, from raster or vector tiles.

**[Documentation](https://jxck-s.github.io/py-staticmaps/)** ·
[Examples](https://jxck-s.github.io/py-staticmaps/examples/) ·
[API reference](https://jxck-s.github.io/py-staticmaps/reference/) ·
[About this fork](https://jxck-s.github.io/py-staticmaps/about.html)

> **This is a fork.** `pip install py-staticmaps` installs
> [the original](https://github.com/flopp/py-staticmaps) from PyPI, which does not
> have the vector tiles, api keys or HiDPI output described below. See
> [About this fork](https://jxck-s.github.io/py-staticmaps/about.html).

## Install

```shell
pip install git+https://github.com/Jxck-S/py-staticmaps
```

With the extras:

```shell
pip install "py-staticmaps[cairo] @ git+https://github.com/Jxck-S/py-staticmaps"   # anti-aliased PNG
pip install "py-staticmaps[pymgl] @ git+https://github.com/Jxck-S/py-staticmaps"   # vector tiles
```

## Use

```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

frankfurt = staticmaps.create_latlng(50.110644, 8.682092)
newyork = staticmaps.create_latlng(40.712728, -74.006015)

context.add_object(staticmaps.Line([frankfurt, newyork], color=staticmaps.BLUE, width=4))
context.add_object(staticmaps.Marker(frankfurt, color=staticmaps.GREEN, size=12))
context.add_object(staticmaps.Marker(newyork, color=staticmaps.RED, size=12))

context.render_pillow(size=(800, 500)).save("frankfurt_newyork.png")
```

![frankfurt_newyork](../assets/frankfurt_newyork.pillow.png?raw=true)

The centre and zoom were computed from the objects, and the line follows a
great circle rather than a straight Mercator segment.

## What it does

- **Objects** — pin markers, image markers, polylines, polygons, geodesic circles
- **Automatic framing** from the objects you added, with optional focus and bounds
- **Predefined raster and vector providers**, most needing no api key — or define your own
- **Three renderers** — anti-aliased PNG via cairo, PNG via Pillow, real SVG
- **Geodesic geometry** on the WGS84 ellipsoid via `geographiclib`
- **On-disc and in-memory tile caching**
- **High-DPI output** for HiDPI displays and print
- A `createstaticmap` command line tool

## Documentation

| | |
|---|---|
| [Installation](https://jxck-s.github.io/py-staticmaps/getting-started/installation.html) | the package and its extras |
| [Your first map](https://jxck-s.github.io/py-staticmaps/getting-started/first-map.html) | end to end |
| [Markers](https://jxck-s.github.io/py-staticmaps/drawing/markers.html) · [Lines](https://jxck-s.github.io/py-staticmaps/drawing/lines.html) · [Areas and circles](https://jxck-s.github.io/py-staticmaps/drawing/areas-and-circles.html) · [Custom objects](https://jxck-s.github.io/py-staticmaps/drawing/custom-objects.html) | what you can draw |
| [Choosing a provider](https://jxck-s.github.io/py-staticmaps/providers/choosing.html) · [API keys](https://jxck-s.github.io/py-staticmaps/providers/api-keys.html) · [Vector tiles](https://jxck-s.github.io/py-staticmaps/providers/vector-tiles.html) · [High-DPI](https://jxck-s.github.io/py-staticmaps/providers/high-dpi.html) | the map underneath |
| [Renderers](https://jxck-s.github.io/py-staticmaps/rendering/renderers.html) · [Size and zoom](https://jxck-s.github.io/py-staticmaps/rendering/size-and-zoom.html) · [Caching](https://jxck-s.github.io/py-staticmaps/rendering/caching.html) · [Focus and bounds](https://jxck-s.github.io/py-staticmaps/rendering/focus-and-bounds.html) | output |
| [Command line](https://jxck-s.github.io/py-staticmaps/cli.html) | `createstaticmap` |

## Development

```shell
make setup            # virtualenv with every dependency
make test             # pytest
make lint             # black, isort, flake8, pylint, mypy, codespell
make run-examples     # render every example into examples/build
make documentation    # build the site
```

`make documentation-serve` serves the docs locally at
[localhost:8000](http://localhost:8000).

## Lineage

```
flopp/py-staticmaps          the original, by Florian Pigorsch
  └─ lowtower/py-staticmaps     a fork that carried it on
       └─ Jxck-S/py-staticmaps     this repository
```

Most of the distance between the original and here is
[lowtower's](https://github.com/lowtower/py-staticmaps) work. See
[About this fork](https://jxck-s.github.io/py-staticmaps/about.html) for what
each layer added and how to install this one.

## License

[MIT](LICENSE).

- Original work copyright (c) 2020 [Florian Pigorsch](https://github.com/flopp)
- Fork work by [Lowtower](https://github.com/lowtower) and
  [Jack Sweeney](https://github.com/Jxck-S)
