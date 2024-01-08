
__all__ = []

try:
    xrange
except NameError:
    xrange = range

import os, multiprocessing
RCM_GRID_ENV = int(os.environ.get('RCM_GRID_ENV',0))
RCM_NO_COLOR = int(os.environ.get('RCM_NO_COLOR',1))
OMP_NUM_THREADS = int(os.environ.get('OMP_NUM_THREADS',multiprocessing.cpu_count()))



from . import gtypes
__all__.extend(gtypes.__all__)
from .gtypes import *

from . import Property
__all__.extend(Property.__all__)
from .Property import *

from . import utilities
__all__.extend(utilities.__all__)
from .utilities import *

from . import messenger
__all__.extend(messenger.__all__)
from .messenger import *

from . import StatusCode
__all__.extend(StatusCode.__all__)
from .StatusCode import *

from . import enumerations
__all__.extend(enumerations.__all__)
from .enumerations import *

from . import parallel
__all__.extend(parallel.__all__)
from .parallel import *

from . import constants
__all__.extend(constants.__all__)
from .constants import *

from . import EventContext
__all__.extend(EventContext.__all__)
from .EventContext import *

from . import Service
__all__.extend(Service.__all__)
from .Service import *

from . import Algorithm
__all__.extend(Algorithm.__all__)
from .Algorithm import *

from . import streamable
__all__.extend(streamable.__all__)
from .streamable import *

from . import tex
__all__.extend(tex.__all__)
from .tex import *

from . import storage
__all__.extend(storage.__all__)
from .storage import *



# Import all root classes
try:
  import ROOT
  useROOT=True
except:
  useROOT=False
  print ('WARNING: ROOT not found. You will not be able to use the TEventLoop, storage and monet  services provied by the gaugi core.')


if useROOT:
  print('Using all sub packages with ROOT dependence')
  from . import TEventLoop
  __all__.extend(TEventLoop.__all__)
  from .TEventLoop import *

  from . import monet
  __all__.extend(monet.__all__)
  from .monet import *

  from . import EDM
  __all__.extend(EDM.__all__)
  from .EDM import *








