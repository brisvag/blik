import pandas as pd
from naaf.writing.mrc import write_mrc
from cryotypes.image import Image
from naaf.writing.star import write_star


def write_image(path, data, attributes):
    img = Image(data=data, pixel_size=attributes['scale'][0], stack=attributes['metadata']['stack'])
    write_mrc(img, str(path), overwrite=True)
    return [path]


def write_particles(path, layer_data):
    dfs = []
    for data, attributes, layer_type in layer_data:
        if layer_type == 'vectors':
            # vector info is actually held in particles, but this makes it
            # convenient to select everything and save
            pass
        elif 'blik_volume' in attributes['metadata']:
            dfs.append(attributes['features'])
        else:
            # for now just ignore other points
            pass

    df = pd.concat(dfs, axis=0, ignore_index=True)
    write_star(df, path, overwrite=True)
    return [path]
