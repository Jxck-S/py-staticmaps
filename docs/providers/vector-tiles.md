# Vector tiles

A vector provider downloads geometry and a [MapLibre GL
style](https://maplibre.org/maplibre-style-spec/), and renders the map
locally.

```python
context.set_tile_provider(staticmaps.tile_provider_OpenFreeMapLiberty)
context.render_pillow(size=(800, 600)).save("map.png")
```

Needs the [`[pymgl]` extra](../getting-started/installation.md#vector-tiles).

## The providers

Several styles across three services, none needing a key. Each was verified
by rendering, not merely by fetching.

| Service | Styles | Factory |
|---|---|---|
| [OpenFreeMap](https://openfreemap.org) | `liberty`, `bright`, `positron`, `dark`, `fiord` | `staticmaps.openfreemap(...)` |
| [Maptoolkit](https://www.maptoolkit.org) | `dark`, `light`, `street` | `staticmaps.maptoolkit(...)` |
| [VersaTiles](https://versatiles.org) | `colorful`, `graybeard`, `neutrino`, `eclipse`, `shadow` | `staticmaps.versatiles(...)` |

Maptoolkit's terms require a visible logo beside the copyright line. The
library renders text attribution only, so meeting that is up to you.

## Any MapLibre style

```python
provider = staticmaps.VectorTileProvider("custom", style_url="https://example.com/style.json")
```

**MapLibre Native trails MapLibre GL JS on the newest style-spec expressions.**
A style using, say, `split` or `global-state` still loads, but the layers
relying on them are skipped *silently* — which can mean a map with no labels
at all. Render any new style once and look at it before relying on it.

## Modifying a style

A style is just JSON, so you can change it before handing it over:

```python
import copy, json, urllib.request

style = json.loads(urllib.request.urlopen(
    urllib.request.Request("https://tiles.openfreemap.org/styles/liberty",
                           headers={"user-agent": "my-app"})).read())

# drop every label layer
no_labels = copy.deepcopy(style)
no_labels["layers"] = [l for l in no_labels["layers"] if l["type"] != "symbol"]

provider = staticmaps.VectorTileProvider(
    "ofm-nolabels", style=no_labels,
    attribution="OpenFreeMap (C) OpenMapTiles Data from OpenStreetMap",
)
```

You can recolour layers, filter features, or inject your own GeoJSON as a
styled layer. Nothing about this is possible with raster tiles.

When you supply a style directly, pass `attribution` too — you are still bound
by the source's licence.

## Headless and GPU-less hosts

pymgl renders through OpenGL but needs **no GPU hardware**: Mesa's `llvmpipe`
rasterises in software. What it does need is a display for the GL stack to
attach to.

```shell
apt-get install -y libegl1 libgl1-mesa-dri xvfb
export LIBGL_ALWAYS_SOFTWARE=1
xvfb-run -a --server-args="-screen 0 1024x768x24 -ac +render -noreset" python your_script.py
```

macOS renders through Metal and needs no xvfb.

**On Debian and Ubuntu you also need a CA symlink.** pymgl's manylinux wheels
are built on a RedHat base, so the curl inside them looks for the CA bundle
where RedHat keeps it and ignores `CURL_CA_BUNDLE`. Without this, every tile
fetch fails with `CApath: none`:

```shell
sudo mkdir -p /etc/pki/tls/certs
sudo ln -sf /etc/ssl/certs/ca-certificates.crt /etc/pki/tls/certs/ca-bundle.crt
```

Without a usable GL stack the process *segfaults* rather than raising, which
cannot be caught in-process — so backend availability is probed in a
subprocess.

## Limits

- `tighten_to_bounds` does not apply; the basemap is rendered as one image
- pymgl fetches its own tiles, so the [on-disc cache](../rendering/caching.md)
  does not help it
- Windows is unsupported
