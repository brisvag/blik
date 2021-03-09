import sys
import argparse
from IPython.terminal.embed import InteractiveShellEmbed

import peepingtom as pt


def parse():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='''
PeepingTom command line interface.

Opens files in napari and lands in an interactive ipython shell
with peepingtom imported as `pt` and the initialised Peeper available as `p`.
''',
                                     epilog='''
mode choices:
  - lone: each datablock in a separate volume
  - zip_by_type: one of each datablock type per volume
  - bunch: all datablocks in a single volume

EXAMPLES

Open a .star file as particles:
  peep particles.star

Open particles and images from a directory:
  peep /dir/with/star_and_mrc_files/

Match files such as MyProtein_10.star and MyProtein_001.mrc,
and name the respective DataBlocks Protein_10 and Protein_001:
  peep /path/to/dir/ -f Protein -n 'Protein_\d+'
''')
    parser.add_argument('paths', nargs='+',
                        help='any number of file or directories')
    parser.add_argument('-m', '--mode', choices=('lone', 'zip_by_type', 'bunch'),
                        help='how to arrange DataBlock into volumes [default: guess from input]')
    parser.add_argument('-f', '--filters',
                        help='a regex used to select filenames [default: .*]')
    parser.add_argument('-n', '--name-regex', metavar='regex',
                        help='a regex used to infer DataBlock names from paths [fallback: \d+]')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='read directories recursively')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='only show the list of files that would be read')
    parser.add_argument('--strict', action='store_true',
                        help='immediately fail if a matched filename cannot be read')
    parser.add_argument('--max', type=int,
                        help='max number of files to read')
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s - PeepingTom {pt.__version__}')
    return parser.parse_args()


def _read_embed(**kwargs):
    sh = InteractiveShellEmbed()
    sh.enable_gui('qt')

    p = pt.read(**kwargs)  # noqa: F841
    sh.push('p')
    sh.run_cell('p.show()')

    sh()


def cli():
    args = parse()
    if args.dry_run:
        files = pt.io_.find_files(args.paths, args.filters, args.recursive, args.max)
        print('Files found:')
        print(*(str(file) for file in files), sep='\n')
        sys.exit()

    kwargs = vars(args)
    kwargs.pop('dry_run')
    _read_embed(**kwargs)
