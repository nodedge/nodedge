import glob
from os.path import basename, dirname, isfile, join

from .add_block import *
from .divide_block import *
from .input_block import *
from .multiply_block import *
from .output_block import *
from .subtract_block import *

# modules = glob.glob(join(dirname(__file__), "*.py"))
# __all__ = [basename(f)[:-3] for f in modules if isfile(f) and f.endswith('_block.py')]
