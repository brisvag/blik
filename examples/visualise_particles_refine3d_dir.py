from pathlib import Path
from peepingtom import data_star_to_crate, Peeper

star_files = list(Path('../tests/test_data/relion_refine3d_directory').glob('*_data.star'))

crates = data_star_to_crate(star_files)

p = Peeper(crates)

p.peep()

