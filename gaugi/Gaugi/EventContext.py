
__all__ = ["EventContext"]

from Gaugi.messenger  import Logger
from Gaugi.gtypes import NotSet
from Gaugi import StatusCode


class EventContext( Logger ):

  def __init__(self, t):
    Logger.__init__(self)
    import collections
    self._containers = collections.OrderedDict()
    self._tree=NotSet
    self._decorations = dict()
    self._current_entry=NotSet
    self._tree = t


  def setHandler(self, key, obj):
    if key in self._containers.keys():
      MSG_ERROR(self, "Key %s exist into the event context. Attach is not possible...",key)
    else:
      self._containers[key]=obj

  def getHandler(self,key):
    return None if not key in self._containers.keys() else self._containers[key]

  def getEntries(self):
    return self._tree.GetEntries()

  def setEntry(self,entry):
    self._current_entry=entry

  def getEntry(self):
    return self._current_entry

  def execute(self):
    self._tree.GetEntry( self.getEntry() )
    for key, edm in self._containers.items():
      if edm.execute().isFailure():
        MSG_WARNING(self,  'Can not execute the edm %s', key )
    return StatusCode.SUCCESS

  def initialize(self):
    return StatusCode.SUCCESS

  def finalize(self):
    return StatusCode.SUCCESS

  def setDecor(self, key, v):
    self._decoration[key] = v

  def getDecor(self,key):
    try:
      return self._decoration[key]
    except KeyError:
      MSG_ERROR(self, 'Decoration %s not found',key)

  def clearDecorations(self):
    self._decoration = dict()

  def decorations(self):
    return self._decoration.keys()






