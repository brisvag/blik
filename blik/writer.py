import pandas as pd
from cryohub.writing.mrc import write_mrc
from cryohub.writing.star import write_star
from cryotypes.image import Image


def write_image(path, data, attributes):
    if 'experiment_id' not in attributes['metadata']:
        raise ValueError('cannot write a layer that does not have blik metadata. Add it to an experiment!')
    img = Image(data=data, experiment_id='', pixel_spacing=attributes['scale'][0], stack=attributes['metadata']['stack'], source='')
    write_mrc(img, str(path), overwrite=True)
    return [path]


def write_particles(path, layer_data):
    dfs = []
    for data, attributes, layer_type in layer_data:
        if layer_type == 'vectors':
            # vector info is actually held in particles, but this makes it
            # convenient to select everything and save
            pass
        elif 'experiment_id' in attributes['metadata']:
            dfs.append(attributes['features'])
        else:
            raise ValueError('cannot write a layer that does not have blik metadata. Add it to an experiment!')

    df = pd.concat(dfs, axis=0, ignore_index=True)
    write_star(df, path, overwrite=True)
    return [path]
