# API keys

Most hosted providers now require a key.

```python
provider = staticmaps.tile_provider_Carto
provider.set_api_key("your-key")
context.set_tile_provider(provider)
```

## Why this has its own page

**A missing key does not always look like an error.** CARTO answers
`HTTP 200` with a perfectly valid PNG that happens to read *"API KEY
REQUIRED"* across the tile. No exception, no status code — just a ruined map
that a script will happily save and publish.

So a provider that needs a key says so, and the library raises rather than
fetching:

```python
staticmaps.tile_provider_Carto.url(14, 2621, 6333)
# ValueError: tile provider "carto" requires an api key; call set_api_key() before rendering
```

Tiles already in the [cache](../rendering/caching.md) are still served, since
they were fetched already.

## One mechanism, several names

Every provider passes the key as a query parameter, and every one calls it
something different. The provider names the parameter; you supply the value.

| Provider | Parameter | Free tier |
|---|---|---|
| [CARTO](https://carto.com/basemaps/apikey) | `key` | 5M tiles/month, non-commercial |
| [Stadia Maps](https://stadiamaps.com) | `api_key` | yes |
| [Jawg](https://www.jawg.io) | `access-token` | yes |

```python
provider.key_param()     # "key"
provider.requires_key()  # True
provider.has_api_key()   # False until you set one
```

## Declaring it on your own provider

```python
staticmaps.TileProvider(
    "my-tiles",
    url_pattern="https://tiles.example.com/$z/$x/$y.png",
    key_param="key",
    requires_key=True,
)
```

The key is appended with the right separator and url-escaped, so the pattern
stays free of key handling.

## Keys from the environment

```python
import os

provider = staticmaps.tile_provider_Carto
api_key = os.environ.get("API_KEY_CARTO")
if api_key:
    provider.set_api_key(api_key)
```

Check for a **non-empty** value rather than `is not None`: a CI workflow sets
an absent secret to an empty string, and an empty key is not a key.

Never commit a key. The bundled examples all read theirs from the
environment.
