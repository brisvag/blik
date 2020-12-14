from ....io_ import read
from ....core import DataCrate, ParticleBlock, stack
from ...depictors import ParticleDepictor
from ..base import Peeper


def peep_particles_together(*file_paths):
    """naively read multiple files containing particle and attempt to visualise common datacrates in the same viewer
    """
    file_contents = [read(file_path) for file_path in file_paths]

    crates = []

    for idx in range(len(file_contents[0])):
        crate = DataCrate()
        for file in file_contents:
            crate += file[idx]
        crates.append(crate)


    peeper = Peeper(crates)
    peeper._init_viewer()
    particlestack = stack(peeper._get_datablocks(ParticleBlock))
    ParticleDepictor(particlestack, peeper=peeper)
    particlestack.depictor.draw()
    return peeper

