# Caching

Fetched raster tiles are written to disc, so re-rendering the same area costs
nothing.

```python
context.set_cache_dir("/tmp/my-tiles")
```

The default is a per-user cache directory chosen by `appdirs`. Files land at:

```
<cache_dir>/<provider name>/<zoom>/<x>/<y>.png
```

The path includes the provider name, so providers never share tiles. Vector
providers fold a hash of the resolved style into their name, because
OpenFreeMap's tile URL carries a dated path that rotates weekly — without it a
rotation would keep serving last week's imagery.

## In-memory caching

For many renders over the same area, the disc cache still costs a file read
per tile. Load a zoom level into memory instead:

```python
context.set_zoom(14)
context.load_tiles_to_mem()
```

Every tile already cached for that level is read once and kept. With
`set_max_min_zoom()` set, every level in the range is loaded.

Memory grows with the size of the cached area, so bound it with
`set_max_min_zoom()` or by keeping the cache directory to the area you care
about. It raises if neither a zoom nor a zoom range has been set, since there
would be no level to load.

## Missing keys and the cache

A cached tile is served without an [api key](../providers/api-keys.md), having
been fetched already. So a provider that would otherwise raise for a missing
key renders happily from cache — worth knowing when a script works on your
machine and fails in CI.

## Vector providers

pymgl fetches its own tiles and caches them internally, so none of the above
applies to it. A fresh render re-parses the style and re-fetches, which is why
a vector map costs around 200 ms against a warm raster map's 10.

## Replacing the downloader

```python
context.set_tile_downloader(my_downloader)
```

Any `TileDownloader` subclass. The test suite uses this to serve fixed bytes
and render without a network; see `tests/mock_tile_downloader.py`.
