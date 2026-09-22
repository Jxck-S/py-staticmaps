#!/usr/bin/env python

"""py-staticmaps - OpenFreeMap pixel ratio example

Renders the same map twice: once at the default density, once at a pixel
ratio of 2. Both cover the identical geographic area; the second simply
draws it with four times as many pixels, which is what a HiDPI display or
a print job wants.

Note that asking for a larger image instead shows *more of the world* at the
same density -- that is a different thing from a higher pixel ratio.
"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import staticmaps

WIDTH, HEIGHT = 800, 600

ferry = staticmaps.create_latlng(37.7955, -122.3937)
coit = staticmaps.create_latlng(37.8024, -122.4058)


def render(ratio: float, filename: str) -> None:
    """Render the same map at a given pixel ratio

    Parameters:
        ratio (float): pixel ratio, 1 for the default density
        filename (str): file to write the png to
    """
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_OpenFreeMapLiberty)
    context.set_pixel_ratio(ratio)

    # Positions scale with the ratio on their own, sizes do not, so scale
    # every pixel dimension to keep the objects in proportion.
    context.add_object(staticmaps.Line([ferry, coit], color=staticmaps.GREEN, width=int(4 * ratio)))
    context.add_object(staticmaps.Marker(ferry, color=staticmaps.RED, size=int(12 * ratio)))
    context.add_object(staticmaps.Marker(coit, color=staticmaps.BLUE, size=int(12 * ratio)))

    context.set_center(staticmaps.create_latlng(37.7990, -122.4000))
    context.set_zoom(15)

    image = context.render_cairo(WIDTH, HEIGHT)
    image.write_to_png(filename)
    print(f"{filename}: {image.get_width()}x{image.get_height()} px at ratio {ratio}")


if staticmaps.cairo_is_supported():
    render(1, "openfreemap.ratio1.cairo.png")
    render(2, "openfreemap.ratio2.cairo.png")
else:
    print('You need to install the "cairo" module to run this example.')
