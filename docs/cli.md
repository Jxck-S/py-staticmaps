# Command line

The package installs a `createstaticmap` command.

```shell
createstaticmap --center 48.005774,7.834042 --zoom 14 --width 800 --height 600 map.png
```

## Options

| Option | Meaning |
|---|---|
| `--center LAT,LNG` | map centre |
| `--zoom N` | zoom level |
| `--width N`, `--height N` | image size in pixels |
| `--tiles NAME` | provider name, e.g. `osm` |
| `--tiles-api-key KEY` | api key for providers that need one |
| `--marker LAT,LNG` | add a marker; repeatable |
| `--line LAT,LNG LAT,LNG ...` | add a line; repeatable |
| `--area LAT,LNG LAT,LNG ...` | add a polygon; repeatable |
| `--bounds LAT,LNG LAT,LNG` | force an area into view |
| `--background COLOR` | background colour |
| `--tight-to-bounds` | crop tiles to the objects (SVG) |
| `--file-format FMT` | output format |

Provider names are the keys of
[`default_tile_providers`](providers/choosing.md#listing-them).

## Examples

A marked point:

```shell
createstaticmap --center 37.7955,-122.3937 --zoom 15 \
  --width 800 --height 600 --marker 37.7955,-122.3937 ferry.png
```

A route, framed automatically:

```shell
createstaticmap --width 800 --height 600 \
  --line 37.7955,-122.3937 37.8024,-122.4058 37.8087,-122.4098 route.png
```

With a provider needing a key:

```shell
createstaticmap --tiles carto --tiles-api-key "$API_KEY_CARTO" \
  --center 48.005,7.834 --zoom 14 --width 800 --height 600 map.png
```

Run `createstaticmap --help` for the authoritative list.
