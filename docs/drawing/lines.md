# Lines

```python
staticmaps.Line(latlngs, color=staticmaps.BLUE, width=2)
```

```python
route = [
    staticmaps.create_latlng(50.110, 8.682),
    staticmaps.create_latlng(40.713, -74.006),
]
context.add_object(staticmaps.Line(route, color=staticmaps.RED, width=3))
```

## Lines are geodesic

This is the part that surprises people, and it is deliberate. A `Line` between
two points follows the **shortest path over the WGS84 ellipsoid** — a great
circle — not a straight segment in the flattened map projection.

So a line from Frankfurt to New York bows north across Greenland, exactly as
an aircraft flies it. Drawing it as a straight Mercator segment would be both
visually wrong and geographically meaningless.

The interpolation happens against `geographiclib`, so the curve is accurate
rather than approximated.

It also means a two-point `Line` is not two points: the library subdivides it
into as many intermediate points as the curve needs at that zoom.

## Crossing the date line

A line whose shortest path crosses ±180° is drawn across it, rather than
wrapped the long way round the map.

That works because the interpolation asks `geographiclib` for *unrolled*
longitudes: a path leaving Japan eastward continues past 180° to 190° instead
of jumping to -170°. Every point on the line is then on a continuous scale,
and the renderer can draw it as one stroke and repeat it either side of the
map edge.

The catch, historically, was the final point. The interpolated points were
unrolled but the endpoint was appended as given — wrapped — so the last
segment leapt from 190° back to -170° and drew a line straight across the
whole map. The endpoint now comes from the same geodesic calculation as the
rest, so it is on the same scale.

The `idl.py` example draws several such lines; see
[Examples](../examples/index.md).

## Width

`width` is in image pixels and does not scale with zoom or pixel density. A
route drawn at `width=3` is three pixels wide at every zoom.

## Many lines

Lines are cheap: cairo draws thousands per second. A map with several thousand
tracks spends nearly all its time fetching tiles, not drawing. See
[Renderers](../rendering/renderers.md#performance).
