from rela.compilation.compiler import RelaCompiler
from rela.language.frontend.frontend import *

def preserve_fe():
    spec = pDot(PStar) % Preserve()
    return RelaCompiler.compile(spec)