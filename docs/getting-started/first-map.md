# Your first map

```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

ferry_building = staticmaps.create_latlng(37.7955, -122.3937)
coit_tower = staticmaps.create_latlng(37.8024, -122.4058)

context.add_object(staticmaps.Line([ferry_building, coit_tower], color=staticmaps.GREEN, width=4))
context.add_object(staticmaps.Marker(ferry_building, color=staticmaps.RED, size=12))
context.add_object(staticmaps.Marker(coit_tower, color=staticmaps.BLUE, size=12))

image = context.render_pillow(size=(800, 600))
image.save("first-map.png")
```

## What happened

**You never set a centre or a zoom.** Both were computed from the objects you
added, so the map frames them with a little room to spare. Set them yourself
when you want a fixed view:

```python
context.set_center(staticmaps.create_latlng(37.799, -122.400))
context.set_zoom(14)
```

**Coordinates are latitude first.** `create_latlng(lat, lng)` — the opposite
order to GeoJSON, which is a common source of maps of the wrong ocean.

**`size` is the image you get.** `render_pillow(size=(800, 600))` produces an
800×600 PNG. See [Size and zoom](../rendering/size-and-zoom.md).

## The three renderers

```python
context.render_pillow(size=(800, 600)).save("map.png")           # PNG, no anti-aliasing
context.render_cairo(size=(800, 600)).write_to_png("map.png")    # PNG, anti-aliased
with open("map.svg", "w", encoding="utf-8") as f:                # real SVG
    context.render_svg(size=(800, 600)).write(f, pretty=True)
```

`render_cairo` needs the [cairo extra](installation.md#anti-aliased-png).

## Next

- [Markers](../drawing/markers.md), [Lines](../drawing/lines.md), [Areas and circles](../drawing/areas-and-circles.md)
- [Choosing a provider](../providers/choosing.md) — the map underneath
