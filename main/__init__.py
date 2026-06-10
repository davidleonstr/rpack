from .commands import *

COMMANDS = {
    'create': rcreate,
    'list': rlist,
    'extract': rextract
}

__all__ = ['COMMANDS']