import click
import napari

import peepingtom


@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('-f', '--force_mode', default=None)
def cli(paths, force_mode=None, **kwargs):
    """Command line entrypoint for the peep function
    """
    with napari.gui_qt():
        return peepingtom.peep(paths, force_mode, **kwargs)
