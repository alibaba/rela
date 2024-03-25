from typing import Dict

import rela.language.regularir.regularir as rir
from .rirspecs import *
from .fespecs import *

defined_specs : Dict[str, rir.Spec] = {
    'preserve': preserve_rir(),
    'preserve_fe': preserve_fe(),
}