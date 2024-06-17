from rela.compilation.compiler import RelaCompiler
from rela.language.frontend.frontend import *

def preserve_fe():
    spec = PStar(pDot) % Preserve()
    return RelaCompiler.compile(spec)