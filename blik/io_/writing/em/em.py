import emfile


def write_em(imageblock, file_path, overwrite=False):
    """
    write an image block to disk as an .em file
    """
    if not file_path.endswith('.em'):
        file_path = file_path + '.em'
    emfile.write(file_path, imageblock.data, header_params={}, overwrite=overwrite)
