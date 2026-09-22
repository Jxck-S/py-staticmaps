[![CI](https://github.com/lowtower/py-staticmaps/workflows/CI/badge.svg)](https://github.com/lowtower/py-staticmaps/actions?query=workflow%3ACI)
[![PyPI Package](https://img.shields.io/pypi/v/py-staticmaps.svg)](https://pypi.org/project/py-staticmaps/)
[![Format](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg?style=flat)](LICENSE)

# py-staticmaps
A python module to create static map images (PNG, SVG) with markers, geodesic lines, etc.

## Features
- Map objects: pin-style markers, image (PNG) markers, polylines, polygons, (geodesic) circles
- Automatic computation of best center + zoom from the added map objects
- Several pre-configured map tile providers
- Vector tile support (OpenFreeMap) rendered via MapLibre Native, with fractional zoom
- Proper tile provider attributions display
- On-disc caching of map tile images for faster drawing and reduced load on the tile servers
- Non-anti-aliased drawing via `PILLOW`
- Anti-aliased drawing via `pycairo` (optional; only if `pycairo` is installed properly)
- SVG creation via `svgwrite`
- optional tightening of the map to object or custom boundaries
  - SVG only
  - tiles are being "cropped" to given boundaries
  - might lead to reduction of image quality

## Installation
### SVG + non-anti-aliased PNG version
```shell
pip install py-staticmaps
```

### SVG + anti-aliased PNG version (via Cairo)
```shell
pip install py-staticmaps[cairo]
```
`py-staticmaps` uses `pycairo` for creating anti-aliased raster-graphics, so make sure `libcairo2` is installed on your system (on Ubuntu just install the `libcairo2-dev` package, i.e. `sudo apt install libcairo2-dev`).

### Vector tiles (OpenFreeMap)
```shell
pip install py-staticmaps[pymgl]
```

## Vector tiles

Raster providers serve pre-rendered image tiles. A vector provider instead downloads
geometry and renders it locally from a MapLibre GL style, which is what
[OpenFreeMap](https://openfreemap.org) publishes. OpenFreeMap needs no API key and
sets no request limits, but attribution is mandatory and is rendered automatically.

```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OpenFreeMapLiberty)
context.add_object(staticmaps.Marker(staticmaps.create_latlng(37.7955, -122.3937)))

context.render_pillow(800, 600).save("map.png")
```

Available styles: `liberty`, `bright`, `positron`, `dark`, `fiord` — either as
`tile_provider_OpenFreeMap*` or via `staticmaps.openfreemap("liberty")`. Any other
MapLibre style works too:

```python
provider = staticmaps.VectorTileProvider("custom", style_url="https://example.com/style.json")
```

### Fractional zoom

Raster tiles exist only at whole zoom levels, so fitting objects to the map has to step
down to the next whole level. A vector style is rendered at an arbitrary scale, so it
fits the bounds exactly:

```python
context.set_zoom(16.47)  # accepted for vector providers
```

Vector tiles also stay sharp well beyond the zoom their data is published at, because
geometry is scaled rather than pixels. OpenFreeMap's data stops at zoom 14 but renders
crisply at zoom 18 and beyond.

### Rendering backend

Vector styles are rendered by [pymgl](https://github.com/brendan-ward/pymgl), which
bundles the MapLibre Native C++ engine, so output matches the reference renderer
including labels, sprites and fill patterns. Wheels are published for macOS (arm64) and
Linux (x86_64, aarch64); **Windows is not supported** — use WSL2 or Docker.

pymgl renders through OpenGL but does **not** require GPU hardware. On a headless or
GPU-less Linux host it works through Mesa's software rasterizer:

```shell
apt-get install -y libegl1 libgl1-mesa-dri xvfb
export LIBGL_ALWAYS_SOFTWARE=1
xvfb-run -a --server-args="-screen 0 1024x768x24 -ac +render -noreset" python your_script.py
```

macOS renders through Metal and needs no xvfb. Without a usable GL stack the process
*segfaults* rather than raising, so availability is probed in a subprocess.

Note that `tighten_to_bounds` and the on-disc tile cache do not apply to vector
providers: the style is rendered as one image, and pymgl fetches its own tiles.

## Examples
Note: PNG support (e.g. `context.render_cairo(...)`) is only available if the `pycairo` module is installed.

### Markers and Geodesic Lines
```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_ArcGISWorldImagery)

warsaw = staticmaps.create_latlng(52.233207, 21.061419)
frankfurt = staticmaps.create_latlng(50.110644, 8.682092)
newyork = staticmaps.create_latlng(40.712728, -74.006015)
los_angeles = staticmaps.create_latlng(33.999099, -118.411735)

context.add_object(staticmaps.Line([frankfurt, newyork], color=staticmaps.BLUE, width=4))
context.add_object(staticmaps.Marker(frankfurt, color=staticmaps.GREEN, size=12))
context.add_object(staticmaps.Marker(newyork, color=staticmaps.RED, size=12))

# render png via pillow
image = context.render_pillow(800, 500)
image.save("frankfurt_newyork.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
if staticmaps.cairo_is_supported():
    cairo_image = context.render_cairo(800, 500)
    cairo_image.write_to_png("frankfurt_newyork.cairo.png")

# render svg
svg_image = context.render_svg(800, 500)
with open("frankfurt_newyork.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

# render png via pillow - tight boundaries
context.set_tighten_to_bounds(True)
image = context.render_pillow(800, 500)
image.save("frankfurt_newyork.tight.pillow.png")

# render png via cairo - tight boundaries
if staticmaps.cairo_is_supported():
    context.set_tighten_to_bounds(True)
    cairo_image = context.render_cairo(800, 500)
    cairo_image.write_to_png("frankfurt_newyork.tight.cairo.png")

# render svg - tight boundaries
context.set_tighten_to_bounds(True)
svg_image = context.render_svg(800, 500)
with open("frankfurt_newyork.tight.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

context2 = staticmaps.Context()
context2.set_tile_provider(staticmaps.tile_provider_CartoDarkNoLabels)
context2.add_object(staticmaps.Marker(frankfurt, color=staticmaps.GREEN, size=12))
context2.add_object(staticmaps.Marker(newyork, color=staticmaps.RED, size=12))
context2.add_object(staticmaps.Bounds([warsaw, los_angeles]))

# render svg
svg_image = context2.render_svg(800, 500)
with open("frankfurt_newyork.warsaw_los_angeles_bounds.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

# render svg - tight boundaries
context2.set_tighten_to_bounds(True)
svg_image = context2.render_svg(800, 500)
with open("frankfurt_newyork.warsaw_los_angeles_bounds.tight.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
```
#### Cairo example
![frankfurt_newyork_cairo](../assets/frankfurt_newyork.cairo.png?raw=true)
#### Pillow example
![frankfurt_newyork_pillow](../assets/frankfurt_newyork.pillow.png?raw=true)
#### SVG example
![frankfurt_newyork_svg](../assets/frankfurt_newyork.svg?raw=true)
#### SVG tight example
![frankfurt_newyork_svg_tight](../assets/frankfurt_newyork.tight.svg?raw=true)
#### SVG custom bounds example (custom bounds of Warsaw and Los Angeles)
![frankfurt_newyork.warsaw_los_angeles_bounds.svg](../assets/frankfurt_newyork.warsaw_los_angeles_bounds.svg?raw=true)
#### SVG custom bounds tight example (custom bounds of Warsaw and Los Angeles)
![frankfurt_newyork.warsaw_los_angeles_bounds.tight.svg](../assets/frankfurt_newyork.warsaw_los_angeles_bounds.tight.svg?raw=true)

### Transparent Polygons
```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

freiburg_polygon = [
    (47.96881, 7.79045),
    (47.96866, 7.78610),
    (47.97134, 7.77874),
    ...
]

context.add_object(
    staticmaps.Area(
        [staticmaps.create_latlng(lat, lng) for lat, lng in freiburg_polygon],
        fill_color=staticmaps.parse_color("#00FF003F"),
        width=2,
        color=staticmaps.BLUE,
    )
)

# render non-anti-aliased png
image = context.render_pillow(800, 500)
image.save("freiburg_area.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 500)
image.write_to_png("freiburg_area.cairo.png")

# render svg
svg_image = context.render_svg(800, 500)
with open("freiburg_area.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
```
#### Cairo example
![freiburg_area_cairo](../assets/freiburg_area.cairo.png?raw=true)
#### SVG tight example
![freiburg_area_svg_tight](../assets/freiburg_area.tight.svg?raw=true)

### Drawing a GPX Track + Image Marker (PNG)
```python
import sys

import gpxpy
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_ArcGISWorldImagery)

with open(sys.argv[1], "r") as file:
    gpx = gpxpy.parse(file)

for track in gpx.tracks:
    for segment in track.segments:
        line = [staticmaps.create_latlng(p.latitude, p.longitude) for p in segment.points]
        context.add_object(staticmaps.Line(line))

for p in gpx.walk(only_points=True):
    pos = staticmaps.create_latlng(p.latitude, p.longitude)
    marker = staticmaps.ImageMarker(pos, "start.png", origin_x=27, origin_y=35)
    context.add_object(marker)
    break

# render png via pillow
image = context.render_pillow(800, 500)
image.save("draw_gpx.pillow.png")

# render png via cairo
if staticmaps.cairo_is_supported():
    image = context.render_cairo(800, 500)
    image.write_to_png("draw_gpx.cairo.png")

# render svg
svg_image = context.render_svg(800, 500)
with open("draw_gpx.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

# render svg - tight boundaries
context.set_tighten_to_bounds(True)
svg_image = context.render_svg(800, 500)
with open("draw_gpx.tight.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
```
#### Cairo example
![draw_gpx_cairo](../assets/running.cairo.png?raw=true)
#### SVG tight example
![draw_gpx_svg_tight](../assets/running.tight.svg?raw=true)

### US State Capitals
```python
import json
import requests
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

URL = (
    "https://gist.githubusercontent.com/jpriebe/d62a45e29f24e843c974/"
    "raw/b1d3066d245e742018bce56e41788ac7afa60e29/us_state_capitals.json"
)
response = requests.get(URL)
for _, data in json.loads(response.text).items():
    capital = staticmaps.create_latlng(float(data["lat"]), float(data["long"]))
    context.add_object(staticmaps.Marker(capital, size=5))

# render non-anti-aliased png
image = context.render_pillow(800, 500)
image.save("us_capitals.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 500)
image.write_to_png("us_capitals.cairo.png")
```
#### Cairo example
![us_capitals_cairo](../assets/us_capitals.cairo.png?raw=true)
#### SVG tight example
![us_capitals_svg_tight](../assets/us_capitals.tight.svg?raw=true)

### Geodesic Circles
```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_StamenToner)

center1 = staticmaps.create_latlng(66, 0)
center2 = staticmaps.create_latlng(0, 0)

context.add_object(staticmaps.Circle(center1, 2000, fill_color=staticmaps.TRANSPARENT, color=staticmaps.RED, width=2))
context.add_object(staticmaps.Circle(center2, 2000, fill_color=staticmaps.TRANSPARENT, color=staticmaps.GREEN, width=2))
context.add_object(staticmaps.Marker(center1, color=staticmaps.RED))
context.add_object(staticmaps.Marker(center2, color=staticmaps.GREEN))

# render non-anti-aliased png
image = context.render_pillow(800, 500)
image.save("geodesic_circles.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 600)
image.write_to_png("geodesic_circles.cairo.png")
```
#### Cairo example
![geodesic_circles_cairo](../assets/geodesic_circles.cairo.png?raw=true)
#### Pillow example
![geodesic_circles_pillow](../assets/geodesic_circles.pillow.png?raw=true)
#### SVG example
![geodesic_circles_svg](../assets/geodesic_circles.svg?raw=true)
#### SVG tight example
![geodesic_circles_svg_tight](../assets/geodesic_circles.tight.svg?raw=true)

### IDL
```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_ArcGISWorldImagery)

hongkong = staticmaps.create_latlng(22.308046, 113.918480)
newyork = staticmaps.create_latlng(40.641766, -73.780968)

context.add_object(staticmaps.Line([hongkong, newyork], color=staticmaps.BLUE))
context.add_object(staticmaps.Marker(hongkong, color=staticmaps.GREEN))
context.add_object(staticmaps.Marker(newyork, color=staticmaps.RED))

# render png via pillow
image = context.render_pillow(1920, 1080)
image.save("idl.pillow.png")

# render png via cairo
if staticmaps.cairo_is_supported():
    cairo_image = context.render_cairo(1920, 1080)
    cairo_image.write_to_png("idl.cairo.png")

# render svg
svg_image = context.render_svg(1920, 1080)
with open("idl.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
```
#### Cairo example
![idl_cairo](../assets/idl.cairo.png?raw=true)
#### Pillow example
![idl_pillow](../assets/idl.pillow.png?raw=true)
#### SVG example
![idl_svg](../assets/idl.svg?raw=true)

### Other Examples
Please take a look at the command line program which uses the `staticmaps` package: `staticmaps/cli.py`

### Dependencies
`py-staticmaps` uses

- `PILLOW` for rendering raster-graphics
- `pycairo` for rendering antialiased raster-graphics (optional!)
- `svgwrite` for writing SVG files
- `s2sphere` for geo coordinates handling
- `geographiclib` for geodesic computations
- `appdirs` for finding the user's default cache directory
- `requests` for downloading tile files

## License
[MIT](LICENSE) &copy; 2020-2025 Florian Pigorsch & Contributors. All rights reserved.
