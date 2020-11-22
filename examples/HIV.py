from peepingtom import ParticlePeeper
import napari

star_file = 'example_data/HIV_15apx.star'
p = ParticlePeeper(star_file)
with napari.gui_qt():
    p.peep()