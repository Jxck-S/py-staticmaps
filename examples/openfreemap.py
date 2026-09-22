#!/usr/bin/env python

"""py-staticmaps - OpenFreeMap vector tile example"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OpenFreeMapLiberty)

# Ferry Building and Coit Tower, San Francisco
ferry_building = staticmaps.create_latlng(37.7955, -122.3937)
coit_tower = staticmaps.create_latlng(37.8024, -122.4058)

context.add_object(staticmaps.Marker(ferry_building, color=staticmaps.RED, size=12))
context.add_object(staticmaps.Marker(coit_tower, color=staticmaps.BLUE, size=12))
context.add_object(staticmaps.Line([ferry_building, coit_tower], color=staticmaps.GREEN, width=4))

image = context.render_pillow(800, 600)
image.save("openfreemap.pillow.png")

svg_image = context.render_svg(800, 600)
with open("openfreemap.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

if staticmaps.cairo_is_supported():
    cairo_image = context.render_cairo(800, 600)
    cairo_image.write_to_png("openfreemap.cairo.png")
