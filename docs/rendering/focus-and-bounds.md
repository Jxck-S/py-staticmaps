# Focus and bounds

Controlling what the automatic framing pays attention to.

## Focused objects

By default the map frames *every* object. Mark some as focused and you can
then frame only those:

```python
context.add_object(staticmaps.Marker(aircraft), focused=True)
context.add_object(staticmaps.Line(track))         # drawn, but not framed on

context.set_focused_only(True)
context.render_pillow(size=(800, 600))
```

Everything is still drawn — focus changes what the framing considers, not what
appears. This suits tracking one object against a busy background: the frame
follows the aircraft while the surrounding traffic stays visible.

```python
context.reset_focused_objects()   # clear the focus set
```

Pair it with [`set_max_min_zoom()`](size-and-zoom.md#constraining-the-automatic-zoom)
when rendering a sequence, or the zoom jumps between frames as the focused
bounds change.

## Bounds objects

`Bounds` takes part in framing without drawing anything:

```python
context.add_object(staticmaps.Bounds([corner_a, corner_b]))
```

Use it to force an area into view — a region you want visible even when no
marker falls inside it.

`extra_pixel_bounds` adds padding, as one number or as
`(left, top, right, bottom)`:

```python
staticmaps.Bounds([a, b], extra_pixel_bounds=(20, 20, 20, 60))
```

## Tightening to bounds

```python
context.set_tighten_to_bounds(True)
```

Crops the rendered tiles to the object bounds instead of filling the canvas,
which trims dead space around a small cluster.

**SVG only**, and not applied to
[vector providers](../providers/vector-tiles.md#limits), whose basemap is a
single image. It may also reduce image quality, since the tiles are scaled to
fit.

## Inspecting the framing

```python
context.object_bounds()                 # every object
context.object_bounds(focused_only=True)
context.extra_pixel_bounds()            # accumulated pixel padding
context.determine_center_zoom(800, 600)
```
