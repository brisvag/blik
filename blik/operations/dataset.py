import numpy as np
import pandas as pd

from ..datablocks import ParticleBlock
from ..dataset import DataSet


def stack_particles_series(dataset):
    """
    stacks a dataset into a time series
    assumes equal number of particles per time step
    """
    all_stacked = []
    for v_name in dataset.volumes.keys():
        particles = dataset[v_name].particles
        rest = [pb for pb in dataset if pb not in particles]
        positions = np.concatenate(particles.positions.data)
        # add a dim to the left and number it
        positions = np.pad(positions, ((0, 0), (1, 0)))
        rng = np.repeat(np.arange(len(particles)), particles[0].n)
        positions[:, 0] = rng
        orientations = np.concatenate(particles.orientations.data)
        properties = pd.concat(particles.properties.data)
        stacked = ParticleBlock(positions_data=positions,
                                orientations_data=orientations,
                                properties_data=properties,
                                volume=v_name)
        all_stacked.append(stacked)
        all_stacked.extend(rest)

    return DataSet(all_stacked)
