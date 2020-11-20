from .particleblock import ParticleBlock


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

        Parameters
        ----------
        particles : ParticleBlock

        Returns
        -------
        transformed_particles : ParticleBlock
                                Shifted, rotated particles

        """
        