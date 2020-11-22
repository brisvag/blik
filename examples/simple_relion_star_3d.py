from peepingtom import data_star_to_crate, ParticlePeeper
import napari

star_file = 'example_data/relion_3d_simple.star'
p = ParticlePeeper(star_file)

with napari.gui_qt():
    p.peep()

