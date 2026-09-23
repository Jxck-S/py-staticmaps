# Choosing a provider

A tile provider is the map underneath your objects.

```python
context.set_tile_provider(staticmaps.tile_provider_OSM)
```

## Raster or vector

**Raster** providers serve pre-rendered PNG tiles. The library fetches them and
composites your objects on top. Fast, universally supported, and the
cartography is fixed by whoever rendered it.

**Vector** providers serve geometry plus a style, rendered locally by
MapLibre. Slower per map, but the style is yours to modify, zoom can be
fractional, and it stays sharp far past the zoom its data is published at.

| | Raster | Vector |
|---|---|---|
| Extra needed | none | `[pymgl]` |
| Typical render | ~10 ms warm | ~200 ms |
| Zoom | whole levels only | [fractional](../rendering/size-and-zoom.md#fractional-zoom) |
| Restyling | no | [yes](vector-tiles.md#modifying-a-style) |
| Windows | yes | no |

Raster is the right default. Reach for vector when you want to restyle the
map, or need sharp output past zoom 19.

## Providers needing no key

| Provider | Constant |
|---|---|
| OpenStreetMap | `tile_provider_OSM` |
| ArcGIS World Imagery | `tile_provider_ArcGISWorldImagery` |
| [OpenFreeMap](https://openfreemap.org) *(vector)* | `tile_provider_OpenFreeMap{Liberty,Bright,Positron,Dark,Fiord}` |
| [Maptoolkit](https://www.maptoolkit.org) *(vector)* | `tile_provider_Maptoolkit{Dark,Light,Street}` |
| [VersaTiles](https://versatiles.org) *(vector)* | `tile_provider_VersaTiles{Colorful,Graybeard,Neutrino,Eclipse,Shadow}` |

## Providers needing a key

CARTO, Stadia Maps and Jawg all require one. See [API keys](api-keys.md).

## Listing them

```python
staticmaps.default_tile_providers          # raster
staticmaps.default_vector_tile_providers   # vector
```

Both are dicts keyed by provider name, so you can iterate them — as
`examples/tile_providers.py` does to render one map per provider.

## Your own provider

The predefined ones are conveniences, not a closed set. Any XYZ tile server or
MapLibre style works.

### Raster

```python
provider = staticmaps.TileProvider(
    "my-tiles",
    url_pattern="https://tiles.example.com/$z/$x/$y.png",
    shards=["a", "b", "c"],
    attribution="Map data (C) Example",
    max_zoom=19,
)
context.set_tile_provider(provider)
```

`$z`, `$x`, `$y` are substituted per tile and `$s` picks a shard from
`shards`. Three optional arguments cover the rest:

| Argument | For |
|---|---|
| `key_param`, `requires_key` | a server needing [an api key](api-keys.md) |
| `tile_size=512` | a server serving [`@2x` tiles](high-dpi.md) |
| `max_zoom` | the deepest zoom it serves |

### Vector

```python
provider = staticmaps.VectorTileProvider("my-style", style_url="https://example.com/style.json")
```

Or hand it a style you built or modified in memory:

```python
provider = staticmaps.VectorTileProvider("my-style", style=style_dict, attribution="...")
```

See [Vector tiles](vector-tiles.md#modifying-a-style).

### Registering it

Nothing requires a provider to be in the predefined dicts — pass it straight
to `set_tile_provider()`. Add it if you want it discoverable alongside the
rest:

```python
staticmaps.default_tile_providers[provider.name()] = provider
```

## Attribution

Every provider carries its attribution, and the renderers draw it
automatically. Most providers require it as a licence condition, so leaving it
on is not optional:

```python
context.render_pillow(size=(800, 600), attribution=False)   # you had better have a reason
```
