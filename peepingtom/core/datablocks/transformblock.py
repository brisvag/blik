import numpy as np

from .particleblock import ParticleBlock
from .pointblock import PointBlock
from .orientationblock import OrientationBlock


class TransformBlock(ParticleBlock):
    """
    A TransformBlock contains a set of 3D transforms described relative
    to their own fixed coordinate system, made up of...
    * positions : (n, 3) array of vectors describing shifts
      to apply as (dx, dy, dz) relative to the origin (0, 0, 0)
    * orientations : (n, 3, 3) array of rotation matrices which
      rotate (by premultiplication) the unit vectors (i, j, k)
    """

    def apply_on(self, particles: ParticleBlock):
        """
        Applies the transforms encoded in this TransformBlock on a
        set of particles in a ParticleBlock

        For m transforms on n particles this results in m x n transformed particles

        Parameters
        ----------
        particles : ParticleBlock

        Returns
        -------
        transformed_particles : ParticleBlock
                                Shifted, rotated particles

        """
        # set up necessary data, be explicit to avoid confusion
        particle_positions = particles.positions.data.reshape(-1, 3, 1)  # (n, 3, 1) array
        particle_orientations = particles.orientations  # (n, 3, 3) array of rotm
        shift_vectors = self.positions.data.reshape(-1, 1, 3, 1)  # (m, 1, 3, 1) array
        transform_orientations = self.orientations.data.reshape(-1, 1, 3, 3)  # (m, 1, 3, 3) array of rotm

        # Orient the shift vectors according to particle orientation
        oriented_shifts = particle_orientations @ shift_vectors  # (m, n, 3, 1)

        # Apply the transformed shifts onto the current particle positions
        output_positions = particle_positions + oriented_shifts  # (m, n, 3, 1)

        # Calculate the new orientations by composing rotations
        #  (n, 3, 3) @ (m, 1, 3, 3) -> (m, n, 3, 3)
        output_orientations = particle_orientations @ transform_orientations

        # replace nan filled matrices with original particle orientations
        # this happens when vectors are already aligned (causes div0)
        output_orientations = np.where(np.isnan(output_orientations), particle_orientations,
                                       output_orientations)

        # Create and return ParticleBlock from output
        points = PointBlock(output_positions.reshape((-1, 3)))
        orientations = OrientationBlock(output_orientations.reshape(-1, 3, 3))

        return ParticleBlock(points, orientations, {})
