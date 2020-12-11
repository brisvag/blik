from setuptools import setup

from peepingtom import __version__

setup(
    name='peepingtom',
    version=f'{__version__}',
    entry_points='''
        [console_scripts]
        peep=peepingtom.entry_points.peep:cli
    '''
)
