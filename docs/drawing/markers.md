# Markers

Four objects mark a single point. All take a `staticmaps.LatLng` first.

| | Shape | Anchored at |
|---|---|---|
| `Marker` | map pin | the point of the pin |
| `Point` | filled circle | its centre |
| `Square` | square, optionally rotated | its centre |
| `ImageMarker` | your own PNG | an origin you choose |

## Marker

```python
staticmaps.Marker(latlng, color=staticmaps.RED, size=10, stroke_width=1)
```

A pin whose tip sits on the coordinate, so it points at the place rather than
covering it. `size` is the pin's radius in pixels; the drawn pin is taller.

```python
context.add_object(staticmaps.Marker(staticmaps.create_latlng(48.005, 7.834)))
context.add_object(staticmaps.Marker(here, color=staticmaps.BLUE, size=14))
```

## Point and Square

```python
staticmaps.Point(latlng, color=staticmaps.RED, size=10, stroke_width=1)
staticmaps.Square(latlng, color=staticmaps.RED, size=10, stroke_width=1, angle=None)
```

Both are centred on the coordinate rather than pointing at it, which suits
data plots better than pins — a scatter of points reads more honestly than a
scatter of pins, because a pin's visual weight sits above its position.

`Square` takes an `angle` in degrees, useful for a heading:

```python
context.add_object(staticmaps.Square(aircraft, color=staticmaps.ORANGE, size=8, angle=bearing))
```

## ImageMarker

```python
staticmaps.ImageMarker(latlng, image, origin_x, origin_y)
```

`image` is a path to a PNG or the bytes of one. `origin_x` and `origin_y` are
the pixel inside your image that should land on the coordinate — so a 48×48
pin whose tip is at the bottom centre uses `origin_x=24, origin_y=48`.

```python
context.add_object(staticmaps.ImageMarker(here, "pin.png", origin_x=24, origin_y=48))
```

## Sizes are pixels, not metres

Every `size` and `stroke_width` is in image pixels, so a marker stays the same
size on screen however far you zoom in. Only [circles](areas-and-circles.md)
are measured on the ground.

This matters when rendering at a higher pixel density: object sizes do **not**
scale with it, so multiply them yourself. See
[High-DPI output](../providers/high-dpi.md).

## Colours

```python
staticmaps.RED, BLUE, GREEN, YELLOW, ORANGE, PURPLE, BROWN, BLACK, WHITE, TRANSPARENT
staticmaps.parse_color("#ff8800")
staticmaps.parse_color("#ff880080")   # with alpha
staticmaps.random_color()
```
