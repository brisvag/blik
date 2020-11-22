from peepingtom import data_star_to_crate, ParticlePeeper

star_file = '../tests/test_data/relion_3d_simple.star'
p = ParticlePeeper(star_file)
p.peep()

# Access properties of layers
particles1 = p.crates[0][0]
particles1.depictor.point_layer.size = 1
particles1.depictor.vector_layer.length = 3
