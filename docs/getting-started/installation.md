# Installation

!!! warning "Not the PyPI package"

    `pip install py-staticmaps` installs
    [the original project](https://github.com/flopp/py-staticmaps), which does
    not have the features described in these docs. See
    [About this fork](../about.md).

```shell
pip install git+https://github.com/Jxck-S/py-staticmaps
```

That gives you SVG output and PNG through Pillow. Everything else is an extra.

## Extras

| Extra | Brings | For |
|---|---|---|
| `[cairo]` | `pycairo` | anti-aliased PNG |
| `[pymgl]` | `pymgl` | vector tile providers |

```shell
pip install "py-staticmaps[cairo] @ git+https://github.com/Jxck-S/py-staticmaps"
pip install "py-staticmaps[pymgl] @ git+https://github.com/Jxck-S/py-staticmaps"
pip install "py-staticmaps[cairo,pymgl] @ git+https://github.com/Jxck-S/py-staticmaps"
```

From a clone, for development:

```shell
git clone https://github.com/Jxck-S/py-staticmaps
cd py-staticmaps
make setup
```

### Anti-aliased PNG

```shell
pip install "py-staticmaps[cairo] @ git+https://github.com/Jxck-S/py-staticmaps"
```

`pycairo` needs the cairo library on your system. On Debian or Ubuntu:

```shell
sudo apt-get install libcairo2-dev
```

Without it you can still render PNGs through Pillow, but object edges are not
anti-aliased — diagonal lines and circles come out stepped. See
[Renderers](../rendering/renderers.md).

### Vector tiles

```shell
pip install "py-staticmaps[pymgl] @ git+https://github.com/Jxck-S/py-staticmaps"
```

`pymgl` bundles the MapLibre Native rendering engine. Wheels are published for
macOS (arm64) and Linux (x86_64, aarch64); **Windows is not supported**, so use
WSL2 or Docker there. Raster providers are unaffected and keep working.

On a headless Linux host it needs a software GL stack; see
[Vector tiles](../providers/vector-tiles.md#headless-and-gpu-less-hosts).

## Checking what you have

```python
import staticmaps

staticmaps.cairo_is_supported()   # True when the cairo extra is installed
```
