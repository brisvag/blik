import click


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('paths', nargs=-1)
@click.option('-m', '--mode', type=click.Choice(['lone', 'zip_by_type', 'bunch']),
              help='how to arrange DataBlock into volumes [default: guess from input]')
@click.option('-n', '--name-regex', metavar='regex',
              help=r'a regex used to infer DataBlock names from paths [fallback: \d+]')
@click.option('-p', '--pixel-size',
              help='manually set the pixel size (overrides the one read from file)')
@click.option('--name', help='the name of the generated DataSet')
@click.option('-d', '--dry-run', is_flag=True,
              help='only show the list of files that would be read')
@click.option('--strict', is_flag=True,
              help='immediately fail if a matched path cannot be read')
@click.option('--lazy', is_flag=True, default=True,
              help='read data lazily (if possible)')
@click.option('--no-show', is_flag=True,
              help='only create the DataSet, without showing the data in napari')
@click.version_option()
def cli(paths, mode, name_regex, pixel_size, dry_run, strict, name, lazy, no_show):
    """
    Blik command line interface.

    Opens files in napari and lands in an interactive ipython shell
    with blik imported and the initialised DataSet available as `dataset`.

    PATHS: any number of files or globs [default='./*']

    \b
    MODE choices:
      - lone: each datablock in a separate volume
      - zip_by_type: one of each datablock type per volume
      - bunch: all datablocks in a single volume

    \b
    EXAMPLES:
    Open a .star file as particles:
        blik particles.star
    Open particles and images from a directory:
        blik /dir/with/star_and_mrc_files/
    Match files such as MyProtein_10.star and MyProtein_001.mrc,
    and name the respective DataBlocks Protein_10 and Protein_001:
        blik /path/to/dir/MyProtein* -n 'Protein_\d+'
    """  # noqa: W605
    if not paths:
        paths = ['./*']

    if dry_run:
        from blik.io_.reading.main import find_files
        files = [str(file) for file in find_files(paths)]
        if files:
            click.echo('Files found:\n' + '\n'.join(files))
        else:
            click.echo('No files found.')
        click.get_current_context().exit()

    import blik
    from IPython.terminal.embed import InteractiveShellEmbed

    dataset = blik.read(*paths,  # noqa: F841
                     name=name,
                     mode=mode,
                     name_regex=name_regex,
                     pixel_size=pixel_size,
                     strict=strict,
                     lazy=lazy,
                     )

    # set up ipython shell nicely
    banner = '''=== Blik ===
initialised variables:
    - dataset
    - viewer
    '''
    sh = InteractiveShellEmbed(banner2=banner)
    sh.enable_gui('qt')
    sh.push('dataset')
    if not no_show:
        sh.run_cell('dataset.show()', silent=True)
    viewer = dataset.napari_viewer  # noqa: F841
    sh.push('viewer')
    sh()
