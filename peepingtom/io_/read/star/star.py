import starfile

from .reader_functions import reader_functions


def read_star(star_path, **kwargs):
    """Dispatch function for reading a starfile into one or multiple ParticleBlocks
    """
    raw_data = starfile.read(star_path, always_dict=True)

    failed_reader_functions = []
    for style, reader_function in reader_functions.items():
        try:
            particle_blocks = reader_function(raw_data, **kwargs)
            return particle_blocks
        except ValueError:
            failed_reader_functions.append((style, reader_function))
    raise ValueError(f'Failed to parse {star_path} using {failed_reader_functions}')
