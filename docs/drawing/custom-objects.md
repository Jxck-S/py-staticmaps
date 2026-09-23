# Custom objects

Anything you draw is a subclass of `staticmaps.Object`. Subclass it when the
built-ins do not fit.

## What to implement

| Method | Purpose |
|---|---|
| `bounds()` | the lat/lng rectangle you occupy, for automatic framing |
| `extra_pixel_bounds()` | padding in pixels, for parts that stick out beyond `bounds()` |
| `render_pillow(renderer)` | draw through Pillow |
| `render_cairo(renderer)` | draw through cairo |
| `render_svg(renderer)` | draw through svgwrite |

`bounds()` and `extra_pixel_bounds()` are what let the map frame itself around
your object. A marker occupies a single coordinate but draws 20 pixels above
it, which is exactly what `extra_pixel_bounds()` is for — without it the pin
would be clipped at the top edge.

You only need the render methods for the renderers you use; the base class
leaves the others as no-ops.

## Sketch

```python
import s2sphere
import staticmaps


class Crosshair(staticmaps.Object):
    def __init__(self, latlng: s2sphere.LatLng, size: int = 12) -> None:
        super().__init__()
        self._latlng = latlng
        self._size = size

    def bounds(self) -> s2sphere.LatLngRect:
        return s2sphere.LatLngRect.from_point(self._latlng)

    def extra_pixel_bounds(self) -> staticmaps.PixelBoundsT:
        return (self._size, self._size, self._size, self._size)

    def render_cairo(self, renderer: staticmaps.CairoRenderer) -> None:
        x, y = renderer.transformer().ll2pixel(self._latlng)
        renderer.context().set_source_rgb(1, 0, 0)
        renderer.context().set_line_width(2)
        renderer.context().move_to(x - self._size, y)
        renderer.context().line_to(x + self._size, y)
        renderer.context().move_to(x, y - self._size)
        renderer.context().line_to(x, y + self._size)
        renderer.context().stroke()
```

`renderer.transformer().ll2pixel(latlng)` is the bridge from coordinates to
pixels, and it is the only thing you need from the transformer in most cases.

A complete worked version, including all three renderers, is in
`examples/custom_objects.py` — see [Examples](../examples/index.md).
