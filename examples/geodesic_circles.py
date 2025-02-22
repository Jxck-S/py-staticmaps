#!/usr/bin/env python

"""py-staticmaps - Example Geodesic Circles"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_StamenToner)

center1 = staticmaps.create_latlng(66, 0)
center2 = staticmaps.create_latlng(0, 0)

context.add_object(staticmaps.Circle(center1, 2000, fill_color=staticmaps.TRANSPARENT, color=staticmaps.RED, width=2))
context.add_object(staticmaps.Circle(center2, 2000, fill_color=staticmaps.TRANSPARENT, color=staticmaps.GREEN, width=2))
context.add_object(staticmaps.Marker(center1))
context.add_object(staticmaps.Marker(center2, color=staticmaps.GREEN))

# render png via pillow
image = context.render_pillow(800, 600)
image.save("geodesic_circles.pillow.png")

# render png via cairo
if staticmaps.cairo_is_supported():
    image = context.render_cairo(800, 600)
    image.write_to_png("geodesic_circles.cairo.png")

# render svg
svg_image = context.render_svg(800, 600)
with open("geodesic_circles.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

# render svg - tight boundaries
context.set_tighten_to_bounds(True)
svg_image = context.render_svg(800, 500)
with open("geodesic_circles.tight.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
