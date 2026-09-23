# Areas and circles

## Area

```python
staticmaps.Area(latlngs, fill_color=staticmaps.TRANSPARENT, color=staticmaps.TRANSPARENT, width=0)
```

A closed polygon. Repeat the first point at the end to close it explicitly.

```python
p1 = staticmaps.create_latlng(48.005, 7.834)
p2 = staticmaps.create_latlng(47.988, 7.868)
p3 = staticmaps.create_latlng(47.985, 7.824)

context.add_object(staticmaps.Area(
    [p1, p2, p3, p1],
    fill_color=staticmaps.parse_color("#00FF003F"),
    color=staticmaps.RED,
    width=2,
))
```

`fill_color` fills it, `color` and `width` outline it. Either can be
`TRANSPARENT` for fill-only or outline-only. A fill with alpha (`#00FF003F`
above) lets the map read through.

Its edges are geodesic, like [lines](lines.md).

## Circle

```python
staticmaps.Circle(center, radius_km, fill_color=..., color=..., width=0)
```

**The radius is in kilometres**, measured on the ground — not pixels. So a
circle keeps its real-world size and *changes* pixel size as you zoom, which
is the opposite of how markers behave.

```python
context.add_object(staticmaps.Circle(
    staticmaps.create_latlng(37.827, -122.423), 0.4,
    fill_color=staticmaps.TRANSPARENT, color=staticmaps.PURPLE, width=3,
))
```

A 0.4 km circle is 400 m across. Passing `400` expecting pixels gives you a
400 km circle, which is usually entirely off the canvas and looks like nothing
rendered at all.

The circle is a true geodesic circle — every point on it is `radius_km` from
the centre across the ellipsoid — so it is drawn as an ellipse away from the
equator, because Mercator stretches with latitude. That is correct, not a bug.

## Bounds

```python
staticmaps.Bounds(latlngs, extra_pixel_bounds=0)
```

An invisible object that takes part in automatic framing without drawing
anything, so you can force the map to include an area. `extra_pixel_bounds`
adds padding, either as one number or as `(left, top, right, bottom)`.

See [Focus and bounds](../rendering/focus-and-bounds.md).
